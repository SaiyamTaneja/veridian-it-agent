"""
Core Agent Logic for Veridian Corp IT Support Agent.
Uses Groq API with Llama 3.3 for intelligent IT support.
"""

import os
import time
from groq import Groq
from knowledge_base import (
    KB_ARTICLES, ASSET_MANAGEMENT_POLICY,
    search_kb, format_kb_for_context, get_all_articles
)
from data_store import (
    EMPLOYEE_REQUESTS, EXISTING_TICKETS,
    format_requests_for_context, format_tickets_for_context,
    get_employee_request
)
from ticket_manager import TicketManager
# Configuration constants (inlined to eliminate external config.py dependency)
import os
try:
    import streamlit as st
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))
except Exception:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.3
GROQ_MAX_TOKENS = 2048

COMPANY_NAME = "Veridian Corp"
CURRENT_WEEK = "Monday 21 September 2026 – Friday 25 September 2026"

CATEGORIES = {
    "password_account": "Password & Account Access",
    "vpn_network": "VPN & Network Access",
    "hardware_laptop": "Hardware — Laptop",
    "hardware_printer": "Hardware — Printer",
    "hardware_equipment": "Hardware — Equipment",
    "software": "Software Installation",
    "email": "Email & Mailbox",
    "security": "Security Incident",
    "access_request": "Access Request",
    "wifi_guest": "Guest Wi-Fi",
    "unclear": "Unclear — Needs Follow-up"
}

SYSTEM_PROMPT = """You are the IT Support Agent for Veridian Corp. The current date context is the week of Monday 21 September 2026 – Friday 25 September 2026.

Your role is to help employees with IT issues by:
1. Understanding their issue clearly
2. Finding the relevant policy or KB article
3. Asking sensible follow-up questions when needed
4. Resolving simple requests directly
5. Escalating risky or unclear requests appropriately
6. Creating structured tickets when needed
7. Always showing which source (KB article or policy) you used
8. Maintaining a clear audit trail

## KNOWLEDGE BASE ARTICLES
{kb_context}

## ASSET MANAGEMENT POLICY
All company-issued hardware, including laptops and monitors, follows a standard 4-year refresh cycle from date of issue. Early replacement outside this cycle requires Finance sign-off in addition to IT approval.
(Source: Asset Management Policy — issued by Finance & Assets, last updated Q2 2026)

## EXISTING TICKET QUEUE (for context and deduplication)
{ticket_context}

## EMPLOYEE REQUESTS QUEUE
{requests_context}

## RULES YOU MUST FOLLOW
1. ONLY use information from the Knowledge Base articles and Asset Management Policy above. Never invent policies.
2. Always cite which KB article (e.g., "Per KB-01: ...") or policy you are referencing.
3. If an issue is unclear, ask follow-up questions — do NOT guess.
4. For security incidents (phishing, malware), ALWAYS escalate to security@veridian-corp.example and warn the employee NOT to forward suspicious emails.
5. Flag unclear ownership rather than inventing it.
6. Check for duplicate tickets in the existing queue before creating new ones.
7. If a request falls outside IT's scope (e.g., Finance-owned systems), redirect the employee to the correct department.
8. For hardware replacement, cross-reference BOTH KB-03 (3-year eligibility) AND the Asset Management Policy (4-year refresh cycle). Note any conflicts.
9. Be professional, empathetic, and concise.
10. When creating a ticket, include: Ticket ID, Employee, Issue Category, Priority, Status, Assigned Action, Source KB, and any Notes.

## RESPONSE FORMAT
When responding to an employee issue, structure your response as:
1. **Acknowledgment** — Briefly acknowledge the issue
2. **Policy Reference** — Cite the relevant KB article(s)
3. **Resolution/Next Steps** — What action to take
4. **Ticket** — If a ticket is needed, create one with structured fields
5. **Follow-up** — Any questions or information needed from the employee
"""

QUERY_SYSTEM_PROMPT = """You are the IT Support Agent for Veridian Corp. You are answering a question about the current state of IT tickets, requests, and policies.

Use the following context to answer questions accurately:

## KNOWLEDGE BASE
{kb_context}

## CURRENT TICKET QUEUE
{ticket_context}

## EMPLOYEE REQUESTS
{requests_context}

## AGENT TICKET LOG
{agent_tickets}

## AUDIT TRAIL
{audit_trail}

Rules:
- Answer based ONLY on the data provided above.
- Always cite sources (KB articles, ticket IDs, request IDs).
- If you don't have enough information to answer, say so clearly.
- Be concise and factual.
"""


class ITSupportAgent:
    """Veridian Corp IT Support Agent powered by Groq LLM."""

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.ticket_manager = TicketManager()
        self.conversation_histories = {}  # employee_email -> list of messages

    def _call_llm(self, messages: list, max_retries: int = 3) -> str:
        """Call Groq LLM with automatic retry on rate limit errors."""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=GROQ_TEMPERATURE,
                    max_tokens=GROQ_MAX_TOKENS
                )
                return response.choices[0].message.content
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e).lower():
                    wait_time = 2 ** attempt + 1  # 2s, 3s, 5s
                    time.sleep(wait_time)
                    continue
                raise e
        raise Exception("Rate limit exceeded after retries. Please wait a moment and try again.")

    def _build_system_prompt(self) -> str:
        """Build the full system prompt with current context."""
        all_articles = get_all_articles()
        kb_context = format_kb_for_context(all_articles)
        ticket_context = format_tickets_for_context()
        requests_context = format_requests_for_context()

        return SYSTEM_PROMPT.format(
            kb_context=kb_context,
            ticket_context=ticket_context,
            requests_context=requests_context
        )

    def _build_query_prompt(self) -> str:
        """Build system prompt for general Q&A queries."""
        all_articles = get_all_articles()
        kb_context = format_kb_for_context(all_articles)
        ticket_context = format_tickets_for_context()
        requests_context = format_requests_for_context()
        agent_tickets = self.ticket_manager.format_tickets_for_context()
        audit_trail = self.ticket_manager.format_audit_trail_for_display()

        return QUERY_SYSTEM_PROMPT.format(
            kb_context=kb_context,
            ticket_context=ticket_context,
            requests_context=requests_context,
            agent_tickets=agent_tickets,
            audit_trail=audit_trail
        )

    def process_employee_request(self, request_id: str) -> str:
        """Process a pre-loaded employee request from the data pack."""
        request = get_employee_request(request_id)
        if not request:
            return f"Request {request_id} not found."

        employee_email = request["employee_email"]
        employee_name = request["employee_name"]
        message = request["request"]

        # Build context-aware prompt for this specific request
        enhanced_message = (
            f"Process this employee request:\n"
            f"Request ID: {request['id']}\n"
            f"Employee: {employee_name} ({employee_email})\n"
            f"Date: {request['date_opened']}\n"
            f"Issue: {message}\n"
            f"Current Action Status: {request['initial_action']}\n\n"
            f"Please analyze this request, cite relevant KB articles, determine the appropriate action "
            f"(resolve, escalate, or follow-up), and create a ticket if needed. "
            f"Include the ticket details in a structured format with these fields:\n"
            f"- Ticket ID (use format TK-XXXX)\n"
            f"- Employee Name and Email\n"
            f"- Issue Category\n"
            f"- Priority (Low/Medium/High/Critical)\n"
            f"- Status\n"
            f"- Assigned To\n"
            f"- Source KB\n"
            f"- Notes\n"
        )

        system_prompt = self._build_system_prompt()

        try:
            agent_response = self._call_llm([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": enhanced_message}
            ])

            # Determine category and priority from response
            category = self._infer_category(message)
            priority = self._infer_priority(message, request)
            status = self._infer_status(agent_response)
            assigned_to = self._infer_assignment(agent_response, category)
            source_kb = self._infer_source_kb(message)

            # Create ticket
            ticket = self.ticket_manager.create_ticket(
                employee_name=employee_name,
                employee_email=employee_email,
                issue_summary=message,
                category=category,
                priority=priority,
                status=status,
                source_kb=source_kb,
                assigned_to=assigned_to,
                notes=f"Request ID: {request_id}. {request['initial_action']}",
                request_id=request_id
            )

            # Handle special cases
            if category == "security":
                self.ticket_manager.escalate_ticket(
                    ticket["id"],
                    reason="Security incident — requires immediate investigation",
                    escalate_to="Security Team (security@veridian-corp.example)",
                    source="KB-09"
                )

            return agent_response

        except Exception as e:
            return f"Error processing request: {str(e)}"

    def chat(self, employee_email: str, employee_name: str, message: str) -> str:
        """Handle a chat message from an employee."""
        if employee_email not in self.conversation_histories:
            self.conversation_histories[employee_email] = []

        history = self.conversation_histories[employee_email]
        history.append({"role": "user", "content": message})

        system_prompt = self._build_system_prompt()

        # Add employee context
        context_message = (
            f"You are chatting with {employee_name} ({employee_email}). "
            f"Respond to their latest message helpfully. "
            f"If they have any existing requests, reference them."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_message}
        ] + history[-10:]  # Keep last 10 messages for context window

        try:
            agent_response = self._call_llm(messages)
            history.append({"role": "assistant", "content": agent_response})

            # Check if this message warrants a ticket or audit entry
            category = self._infer_category(message)
            priority = self._infer_priority(message, {})
            source_kb = self._infer_source_kb(message)
            status = self._infer_status(agent_response)
            assigned_to = self._infer_assignment(agent_response, category)

            existing_dup = self.ticket_manager.check_duplicate(message, employee_email)
            if not existing_dup and category != "unclear":
                t = self.ticket_manager.create_ticket(
                    employee_name=employee_name,
                    employee_email=employee_email,
                    issue_summary=message,
                    category=category,
                    priority=priority,
                    status=status,
                    source_kb=source_kb,
                    assigned_to=assigned_to,
                    notes="Created via interactive chat"
                )
                if category == "security":
                    self.ticket_manager.escalate_ticket(
                        t["id"],
                        reason="Security incident reported in chat — requires immediate investigation",
                        escalate_to="Security Team (security@veridian-corp.example)",
                        source="KB-09"
                    )
            else:
                self.ticket_manager._add_audit_entry(
                    ticket_id=existing_dup["id"] if existing_dup else "CHAT-LOG",
                    action="CHAT_INTERACTION",
                    details=f"Chat from {employee_name}: {message[:100]}",
                    source=source_kb,
                    decision=f"Status: {status}, Category: {category}"
                )

            return agent_response

        except Exception as e:
            error_msg = f"I'm sorry, I encountered an error: {str(e)}. Please try again."
            history.append({"role": "assistant", "content": error_msg})
            return error_msg

    def query(self, question: str) -> str:
        """Handle a general query about tickets, requests, or policies."""
        system_prompt = self._build_query_prompt()

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            return self._call_llm(messages)

        except Exception as e:
            return f"Error processing query: {str(e)}"

    def process_all_requests(self) -> dict:
        """Process all pre-loaded employee requests and return results."""
        results = {}
        for req in EMPLOYEE_REQUESTS:
            result = self.process_employee_request(req["id"])
            results[req["id"]] = {
                "employee": req["employee_name"],
                "request": req["request"],
                "response": result
            }
        return results

    def get_daily_brief(self) -> str:
        """Generate a daily brief of all ticket activity."""
        prompt = (
            "Generate a concise Daily IT Support Brief for today. Include:\n"
            "1. Summary of open/active requests\n"
            "2. Items needing immediate action\n"
            "3. Items waiting on approvals\n"
            "4. Escalated security incidents\n"
            "5. Resolved items\n"
            "6. Items needing follow-up from employees\n\n"
            "Use the employee requests and ticket data provided in your context. "
            "Be concise and actionable."
        )
        return self.query(prompt)

    def _infer_category(self, message: str) -> str:
        """Infer issue category from message."""
        msg = message.lower()
        if any(w in msg for w in ["password", "locked", "locked out", "login", "log in", "account"]):
            if "expense" in msg:
                return "software"  # Expense tool login issue
            return "password_account"
        if any(w in msg for w in ["vpn", "remote access"]):
            return "vpn_network"
        if any(w in msg for w in ["laptop", "screen", "hardware", "dead", "flickering", "won't turn on"]):
            return "hardware_laptop"
        if any(w in msg for w in ["printer", "print", "paper jam"]):
            return "hardware_printer"
        if any(w in msg for w in ["monitor", "chair", "home office", "work from home", "wfh", "equipment"]):
            return "hardware_equipment"
        if any(w in msg for w in ["software", "install", "application", "tool", "browser", "extension", "catalog"]):
            return "software"
        if any(w in msg for w in ["email", "mailbox", "quota", "mail", "send email"]):
            return "email"
        if any(w in msg for w in ["phishing", "malware", "security", "suspicious", "hack", "virus"]):
            return "security"
        if any(w in msg for w in ["access", "admin", "permission", "server"]):
            return "access_request"
        if any(w in msg for w in ["wifi", "wi-fi", "guest", "wireless"]):
            return "wifi_guest"
        if any(w in msg for w in ["expense"]):
            return "software"  # Expense tool = redirect to Finance
        return "unclear"

    def _infer_priority(self, message: str, request: dict) -> str:
        """Infer priority from message content."""
        msg = message.lower()
        if any(w in msg for w in ["phishing", "malware", "security", "hack", "virus", "unauthorized"]):
            return "Critical"
        if any(w in msg for w in ["urgent", "immediately", "can't work", "dead", "locked out", "can't send"]):
            return "High"
        if any(w in msg for w in ["expired", "full", "flickering", "admin access"]):
            return "Medium"
        return "Medium"

    def _infer_status(self, response: str) -> str:
        """Infer ticket status from agent response."""
        resp = response.lower()
        if any(w in resp for w in ["escalat"]):
            return "Escalated"
        if any(w in resp for w in ["resolved", "no ticket required", "self-service"]):
            return "Resolved"
        if any(w in resp for w in ["waiting", "pending", "approval"]):
            return "Pending"
        if any(w in resp for w in ["follow-up", "clarif", "more information"]):
            return "Awaiting Info"
        return "Open"

    def _infer_assignment(self, response: str, category: str) -> str:
        """Infer who the ticket should be assigned to."""
        resp = response.lower()
        if "security" in resp and category == "security":
            return "Security Team"
        if "finance" in resp:
            return "Finance Department"
        if "manager" in resp:
            return "Employee's Manager"
        return "IT Support"

    def _infer_source_kb(self, message: str) -> str:
        """Infer which KB articles are relevant."""
        articles = search_kb(message)
        if articles:
            return ", ".join([a["id"] for a in articles[:3]])
        return "Manual Review Required"
