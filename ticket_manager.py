"""
Ticket Manager for Veridian Corp IT Support Agent.
Handles ticket creation, updates, resolution, escalation, and audit trail.
"""

import json
from datetime import datetime
from typing import Optional


class TicketManager:
    """Manages IT support tickets with full audit trail."""

    def __init__(self):
        self.tickets = {}  # ticket_id -> ticket dict
        self.audit_log = []  # list of audit entries
        self.next_ticket_num = 1052  # Continue from existing TK-1051

    def create_ticket(
        self,
        employee_name: str,
        employee_email: str,
        issue_summary: str,
        category: str,
        priority: str = "Medium",
        status: str = "Open",
        source_kb: str = "",
        assigned_to: str = "IT Support",
        notes: str = "",
        request_id: str = ""
    ) -> dict:
        """Create a new support ticket."""
        ticket_id = f"TK-{self.next_ticket_num}"
        self.next_ticket_num += 1

        ticket = {
            "id": ticket_id,
            "request_id": request_id,
            "employee_name": employee_name,
            "employee_email": employee_email,
            "issue_summary": issue_summary,
            "category": category,
            "priority": priority,
            "status": status,
            "source_kb": source_kb,
            "assigned_to": assigned_to,
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "resolution": None,
            "history": []
        }

        ticket["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Ticket Created",
            "details": f"Created for {employee_name}: {issue_summary}",
            "source": source_kb
        })

        self.tickets[ticket_id] = ticket

        self._add_audit_entry(
            ticket_id=ticket_id,
            action="TICKET_CREATED",
            details=f"New ticket for {employee_name} ({employee_email}): {issue_summary}",
            source=source_kb,
            decision=f"Category: {category}, Priority: {priority}, Assigned to: {assigned_to}"
        )

        return ticket

    def update_ticket(self, ticket_id: str, updates: dict) -> Optional[dict]:
        """Update an existing ticket."""
        if ticket_id not in self.tickets:
            return None

        ticket = self.tickets[ticket_id]
        changes = []

        for key, value in updates.items():
            if key in ticket and ticket[key] != value:
                changes.append(f"{key}: '{ticket[key]}' → '{value}'")
                ticket[key] = value

        ticket["updated_at"] = datetime.now().isoformat()
        ticket["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Ticket Updated",
            "details": "; ".join(changes) if changes else "No changes",
            "source": updates.get("source_kb", "")
        })

        self._add_audit_entry(
            ticket_id=ticket_id,
            action="TICKET_UPDATED",
            details="; ".join(changes),
            source=updates.get("source_kb", "")
        )

        return ticket

    def resolve_ticket(self, ticket_id: str, resolution: str, source: str = "") -> Optional[dict]:
        """Resolve a ticket with a resolution note."""
        if ticket_id not in self.tickets:
            return None

        ticket = self.tickets[ticket_id]
        ticket["status"] = "Resolved"
        ticket["resolution"] = resolution
        ticket["updated_at"] = datetime.now().isoformat()
        ticket["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Ticket Resolved",
            "details": resolution,
            "source": source
        })

        self._add_audit_entry(
            ticket_id=ticket_id,
            action="TICKET_RESOLVED",
            details=resolution,
            source=source
        )

        return ticket

    def escalate_ticket(self, ticket_id: str, reason: str, escalate_to: str, source: str = "") -> Optional[dict]:
        """Escalate a ticket to another team/person."""
        if ticket_id not in self.tickets:
            return None

        ticket = self.tickets[ticket_id]
        ticket["status"] = f"Escalated to {escalate_to}"
        ticket["assigned_to"] = escalate_to
        ticket["priority"] = "High"
        ticket["updated_at"] = datetime.now().isoformat()
        ticket["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "Ticket Escalated",
            "details": f"Escalated to {escalate_to}: {reason}",
            "source": source
        })

        self._add_audit_entry(
            ticket_id=ticket_id,
            action="TICKET_ESCALATED",
            details=f"Escalated to {escalate_to}: {reason}",
            source=source,
            decision=f"Escalation required — {reason}"
        )

        return ticket

    def get_ticket(self, ticket_id: str) -> Optional[dict]:
        """Get a ticket by ID."""
        return self.tickets.get(ticket_id)

    def get_all_tickets(self) -> list:
        """Get all tickets."""
        return list(self.tickets.values())

    def get_active_tickets(self) -> list:
        """Get all non-resolved tickets."""
        return [t for t in self.tickets.values() if t["status"] not in ["Resolved", "Rejected"]]

    def get_tickets_by_employee(self, employee_email: str) -> list:
        """Get all tickets for a specific employee."""
        return [t for t in self.tickets.values() if t["employee_email"] == employee_email]

    def get_audit_trail(self) -> list:
        """Get the complete audit trail."""
        return self.audit_log

    def format_tickets_for_display(self) -> str:
        """Format all agent-created tickets for display."""
        if not self.tickets:
            return "No tickets created yet."

        lines = []
        for ticket in self.tickets.values():
            lines.append(
                f"**[{ticket['status'].upper()}] {ticket['id']}** | {ticket['employee_name']}\n"
                f"   Issue: {ticket['issue_summary']}\n"
                f"   Category: {ticket['category']}\n"
                f"   Priority: {ticket['priority']}\n"
                f"   Status: {ticket['status']}\n"
                f"   Assigned: {ticket['assigned_to']}\n"
                f"   Source: {ticket['source_kb']}\n"
                f"   Notes: {ticket['notes']}\n"
                f"   Created: {ticket['created_at']}"
            )
            if ticket['resolution']:
                lines[-1] += f"\n   Resolution: {ticket['resolution']}"
        return "\n\n".join(lines)

    def format_audit_trail_for_display(self) -> str:
        """Format audit trail for display."""
        if not self.audit_log:
            return "No audit entries yet."

        lines = []
        for entry in self.audit_log:
            lines.append(
                f"[{entry['action']}] {entry['timestamp']}\n"
                f"   Ticket: {entry['ticket_id']}\n"
                f"   Action: {entry['action']}\n"
                f"   Details: {entry['details']}\n"
                f"   Source: {entry.get('source', 'N/A')}\n"
                f"   Decision: {entry.get('decision', 'N/A')}"
            )
        return "\n\n".join(lines)

    def format_tickets_for_context(self) -> str:
        """Format tickets for LLM context."""
        if not self.tickets:
            return "No agent-created tickets yet."

        lines = []
        for ticket in self.tickets.values():
            lines.append(
                f"• {ticket['id']} | {ticket['employee_name']} | "
                f"{ticket['issue_summary']} | Status: {ticket['status']} | "
                f"Source: {ticket['source_kb']}"
            )
        return "\n".join(lines)

    def _add_audit_entry(
        self,
        ticket_id: str,
        action: str,
        details: str,
        source: str = "",
        decision: str = ""
    ):
        """Add an entry to the audit trail."""
        self.audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "ticket_id": ticket_id,
            "action": action,
            "details": details,
            "source": source,
            "decision": decision
        })

    def check_duplicate(self, issue_summary: str, employee_email: str) -> Optional[dict]:
        """Check if a similar ticket already exists for this employee."""
        # Check agent-created tickets
        for ticket in self.tickets.values():
            if (ticket["employee_email"] == employee_email and
                    ticket["status"] not in ["Resolved", "Rejected"]):
                # Simple keyword overlap check
                existing_words = set(ticket["issue_summary"].lower().split())
                new_words = set(issue_summary.lower().split())
                overlap = existing_words & new_words
                # If more than 40% words overlap, likely duplicate
                if len(overlap) > 0.4 * max(len(existing_words), len(new_words), 1):
                    return ticket
        return None

    def export_to_json(self) -> str:
        """Export all tickets and audit trail as JSON."""
        return json.dumps({
            "tickets": list(self.tickets.values()),
            "audit_log": self.audit_log
        }, indent=2, default=str)
