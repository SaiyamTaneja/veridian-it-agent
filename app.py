"""
Veridian Corp IT Support Agent - Interactive Prototype
Built for AIONOS Assignment 2: Internal Service Agent (IT Support)
"""

import streamlit as st
import os
import json
from agent_core import ITSupportAgent, COMPANY_NAME, CURRENT_WEEK, GROQ_API_KEY
from data_store import EMPLOYEE_REQUESTS, EXISTING_TICKETS
from knowledge_base import KB_ARTICLES, ASSET_MANAGEMENT_POLICY


def init_session_state():
    """Initialize session state variables."""
    if "agent" not in st.session_state:
        st.session_state.agent = ITSupportAgent(api_key=GROQ_API_KEY)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}

    if "processed_requests" not in st.session_state:
        st.session_state.processed_requests = {}


def render_sidebar():
    """Render sidebar with 4 focused pages."""
    with st.sidebar:
        st.title("Veridian Corp")
        st.caption("IT Support Agent - Assignment 2")
        st.markdown(f"**Context Week:** {CURRENT_WEEK}")
        st.divider()

        st.success("Agent Active")
        st.divider()

        page = st.radio(
            "Navigation",
            [
                "Employee Chat",
                "Requests & Tickets",
                "Audit Trail",
                "Knowledge Base"
            ],
            index=0
        )
        st.divider()

    return page


def render_chat_page():
    """Page 1: Conversational Employee IT Support."""
    st.header("IT Support Chat")
    st.markdown("Interactive agent interface: chat as any employee from the data pack or test custom scenarios.")

    employees = [(r["employee_name"], r["employee_email"]) for r in EMPLOYEE_REQUESTS]
    employees.insert(0, ("-- Select an employee --", ""))
    employees.append(("Custom Employee", "custom"))

    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.selectbox(
            "Chat as:",
            options=range(len(employees)),
            format_func=lambda i: f"{employees[i][0]} ({employees[i][1]})" if employees[i][1] else employees[i][0]
        )

    employee_name = employees[selected][0]
    employee_email = employees[selected][1]

    if employee_email == "custom":
        col1, col2 = st.columns(2)
        with col1:
            employee_name = st.text_input("Name", value="Test Employee")
        with col2:
            employee_email = st.text_input("Email", value="test@veridian-corp.example")

    if not employee_email or employee_email == "":
        st.info("Select an employee above to start chatting.")
        return

    # Show context card for existing request if matched
    for req in EMPLOYEE_REQUESTS:
        if req["employee_email"] == employee_email:
            with st.expander(f"Data Pack Record: {req['id']} ({req['date_opened']})", expanded=False):
                st.markdown(f"**Existing Request:** {req['request']}")
                st.markdown(f"**Current Status:** {req['initial_action']}")
            break

    st.divider()

    # Chat history
    if employee_email not in st.session_state.chat_history:
        st.session_state.chat_history[employee_email] = []

    for msg in st.session_state.chat_history[employee_email]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input(f"Type message as {employee_name.split()[0]}..."):
        st.session_state.chat_history[employee_email].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Agent evaluating policies and history..."):
                response = st.session_state.agent.chat(employee_email, employee_name, prompt)
            st.markdown(response)

        st.session_state.chat_history[employee_email].append({"role": "assistant", "content": response})
        st.rerun()


def render_requests_and_tickets():
    """Page 2: Process Requests & Ticket Queue with inline cards."""
    st.header("Requests & Tickets")
    st.markdown("Process all 15 employee requests from the data pack (REQ-01 to REQ-15) and view structured tickets inline.")

    # Top Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Requests", len(EMPLOYEE_REQUESTS))
    with col2:
        st.metric("Processed", len(st.session_state.processed_requests))
    with col3:
        agent_tickets_count = len(st.session_state.agent.ticket_manager.tickets) if st.session_state.agent else 0
        st.metric("Agent Tickets Created", agent_tickets_count)

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("Process All 15 Requests", type="primary", use_container_width=True):
            prog = st.progress(0)
            status_text = st.empty()
            for idx, req in enumerate(EMPLOYEE_REQUESTS):
                if req["id"] not in st.session_state.processed_requests:
                    status_text.text(f"Processing {req['id']} ({req['employee_name']})...")
                    res = st.session_state.agent.process_employee_request(req["id"])
                    st.session_state.processed_requests[req["id"]] = res
                prog.progress((idx + 1) / len(EMPLOYEE_REQUESTS))
            status_text.text("All 15 requests evaluated and triaged.")
            st.rerun()

    st.divider()

    # Requests List with inline ticket cards
    st.subheader("Employee Requests (REQ-01 to REQ-15)")

    for req in EMPLOYEE_REQUESTS:
        is_done = req["id"] in st.session_state.processed_requests
        status_tag = "[COMPLETED]" if is_done else f"[{req['status'].upper()}]"

        with st.expander(f"{status_tag} {req['id']} — {req['employee_name']} | {req['date_opened']}", expanded=False):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown(f"**Employee:** {req['employee_name']} ({req['employee_email']})")
                st.markdown(f"**Request:** {req['request']}")
                st.markdown(f"**Initial Action So Far:** {req['initial_action']}")
            with c2:
                if not is_done:
                    if st.button("Process Request", key=f"btn_{req['id']}", use_container_width=True):
                        with st.spinner(f"Evaluating {req['id']}..."):
                            res = st.session_state.agent.process_employee_request(req["id"])
                            st.session_state.processed_requests[req["id"]] = res
                        st.rerun()

            if is_done:
                st.divider()
                st.markdown("#### Agent Resolution & Policy Grounding")
                st.markdown(st.session_state.processed_requests[req["id"]])

                # Inline Ticket Details if created
                matching_tickets = [
                    t for t in st.session_state.agent.ticket_manager.tickets.values()
                    if t.get("request_id") == req["id"] or t.get("employee_email") == req["employee_email"]
                ]
                if matching_tickets:
                    latest_ticket = matching_tickets[-1]
                    st.markdown("#### Structured Ticket Card")
                    card_content = (
                        f"**Ticket ID:** {latest_ticket['id']} | **Status:** {latest_ticket['status']} | **Priority:** {latest_ticket['priority']}\n\n"
                        f"**Category:** {latest_ticket['category']} | **Assigned To:** {latest_ticket['assigned_to']}\n\n"
                        f"**Policy Source:** {latest_ticket['source_kb']} | **Created:** {latest_ticket['created_at']}\n\n"
                        f"**Notes:** {latest_ticket['notes']}"
                    )
                    st.info(card_content)

    st.divider()

    # Historical Queue Section for precedent context
    with st.expander("Historical Ticketing System Queue (TK-1042 to TK-1051 Precedents)", expanded=False):
        st.markdown("The pre-existing tickets provided in the data pack used by the agent for precedent and consistency:")
        for t in EXISTING_TICKETS:
            tag = "[Closed]" if not t["is_active"] else "[Active]"
            st.markdown(f"• **{t['id']}** ({tag}) | **{t['employee_name']}** | {t['issue_summary']} — *Status: {t['status']}*")
            if t.get("resolution"):
                st.caption(f"  Precedent Note: {t['resolution']}")


def render_audit_trail():
    """Page 3: Comprehensive Audit Trail & Provenance."""
    st.header("Audit Trail")
    st.markdown("Immutable record of all agent actions, policy sources cited, and triage decisions.")

    if st.session_state.agent and st.session_state.agent.ticket_manager.audit_log:
        audit_log = st.session_state.agent.ticket_manager.get_audit_trail()

        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Total Audit Events Logged", len(audit_log))
        with col2:
            json_export = json.dumps(audit_log, indent=2, default=str)
            st.download_button(
                "Download Audit Log (JSON)",
                data=json_export,
                file_name="veridian_it_audit_trail.json",
                mime="application/json"
            )

        actions = list(set(e["action"] for e in audit_log))
        selected_actions = st.multiselect("Filter by Action:", actions, default=actions)

        for entry in reversed(audit_log):
            if entry["action"] not in selected_actions:
                continue

            with st.expander(f"[{entry['action']}] {entry['ticket_id']} | {entry['timestamp']}", expanded=False):
                st.markdown(f"**Ticket / Reference:** {entry['ticket_id']}")
                st.markdown(f"**Action Executed:** {entry['action']}")
                st.markdown(f"**Details:** {entry['details']}")
                st.markdown(f"**Governing Source:** {entry.get('source', 'N/A')}")
                st.markdown(f"**Agent Decision Rationale:** {entry.get('decision', 'N/A')}")
                st.markdown(f"**Timestamp:** {entry['timestamp']}")
    else:
        st.info("No audit entries yet. Interact with the chat or process requests to populate the audit trail.")


def render_knowledge_base():
    """Page 4: Grounding Knowledge Base & Asset Policy."""
    st.header("Knowledge Base & Policies")
    st.markdown("Official Veridian Corp policies governing all agent reasoning (zero-hallucination constraint).")

    for article_id, article in KB_ARTICLES.items():
        with st.expander(f"{article['id']}: {article['title']}"):
            st.markdown(f"**Category:** {article['category']}")
            st.markdown(f"**Content:** {article['content']}")
            st.markdown(f"**Resolution Type:** {article['resolution_type']}")
            st.markdown(f"**Requires Approval:** {article['requires_approval']}")
            st.caption(f"Keywords: {', '.join(article['keywords'])}")

    st.divider()
    with st.expander("Asset Management Policy (Finance & Assets Extract - Q2 2026)", expanded=True):
        st.markdown(f"**Issued By:** {ASSET_MANAGEMENT_POLICY['issued_by']} | **Updated:** {ASSET_MANAGEMENT_POLICY['last_updated']}")
        st.markdown(f"**Policy Text:** {ASSET_MANAGEMENT_POLICY['content']}")
        st.caption("Note: Laptops & monitors follow 4-year refresh cycle. Early replacement requires Finance sign-off in addition to IT approval.")


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="Veridian Corp IT Support Agent",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .stExpander {
            border: 1px solid #334155;
            border-radius: 8px;
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    init_session_state()
    page = render_sidebar()

    if page == "Employee Chat":
        render_chat_page()
    elif page == "Requests & Tickets":
        render_requests_and_tickets()
    elif page == "Audit Trail":
        render_audit_trail()
    elif page == "Knowledge Base":
        render_knowledge_base()


if __name__ == "__main__":
    main()
