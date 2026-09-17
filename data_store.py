"""
Data Store for Veridian Corp IT Support Agent.
Contains pre-loaded employee requests and existing ticket queue.
Company context: Week of Monday 21 Sep 2026 – Friday 25 Sep 2026.
"""

EMPLOYEE_REQUESTS = [
    {
        "id": "REQ-01",
        "employee_name": "Aditi Sharma",
        "employee_email": "aditi.sharma@veridian-corp.example",
        "date_opened": "Mon 21 Sep 2026",
        "request": "My laptop won't turn on at all, it's completely dead, had it about 3.5 years now.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-02",
        "employee_name": "Vikram Chawla",
        "employee_email": "vikram.chawla@veridian-corp.example",
        "date_opened": "Mon 21 Sep 2026",
        "request": "Can I get Wi-Fi access for a guest visiting our office tomorrow?",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-03",
        "employee_name": "Karan Mehta",
        "employee_email": "karan.mehta@veridian-corp.example",
        "date_opened": "Mon 21 Sep 2026",
        "request": "I'm locked out of my account, tried my password 6 times.",
        "initial_action": "In progress — reset queued",
        "status": "in_progress"
    },
    {
        "id": "REQ-04",
        "employee_name": "Ritu Bhatia",
        "employee_email": "ritu.bhatia@veridian-corp.example",
        "date_opened": "Tue 22 Sep 2026",
        "request": "Need approval to install a data-analysis tool that's not in the software catalog.",
        "initial_action": "Waiting on Security review",
        "status": "in_progress"
    },
    {
        "id": "REQ-05",
        "employee_name": "Sanjay Oberoi",
        "employee_email": "sanjay.oberoi@veridian-corp.example",
        "date_opened": "Tue 22 Sep 2026",
        "request": "My VPN stopped working this morning, says credentials expired.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-06",
        "employee_name": "Meera Iyer",
        "employee_email": "meera.iyer@veridian-corp.example",
        "date_opened": "Tue 22 Sep 2026",
        "request": "Printer on the 3rd floor keeps showing 'paper jam' even though there's no jam.",
        "initial_action": "Investigating — technician assigned",
        "status": "in_progress"
    },
    {
        "id": "REQ-07",
        "employee_name": "Farhan Ali",
        "employee_email": "farhan.ali@veridian-corp.example",
        "date_opened": "Wed 23 Sep 2026",
        "request": "I've started working from home 4 days a week, how do I get a monitor?",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-08",
        "employee_name": "Ananya Reddy",
        "employee_email": "ananya.reddy@veridian-corp.example",
        "date_opened": "Wed 23 Sep 2026",
        "request": "I think I got a phishing email asking for my login — forwarding it to a few teammates to check.",
        "initial_action": "Escalated to Security (auto-flagged)",
        "status": "escalated"
    },
    {
        "id": "REQ-09",
        "employee_name": "Rohit Desai",
        "employee_email": "rohit.desai@veridian-corp.example",
        "date_opened": "Wed 23 Sep 2026",
        "request": "My mailbox is full and I can't send emails.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-10",
        "employee_name": "Kavya Pillai",
        "employee_email": "kavya.pillai@veridian-corp.example",
        "date_opened": "Wed 23 Sep 2026",
        "request": "Can someone give me admin access to the finance reporting server? Need it urgently for month-end.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-11",
        "employee_name": "Nikhil Bansal",
        "employee_email": "nikhil.bansal@veridian-corp.example",
        "date_opened": "Thu 24 Sep 2026",
        "request": "New contractor joining my team next week, they'll need VPN access.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-12",
        "employee_name": "Sneha Kulkarni",
        "employee_email": "sneha.kulkarni@veridian-corp.example",
        "date_opened": "Thu 24 Sep 2026",
        "request": "I can't log into the expense tool, keeps saying invalid credentials.",
        "initial_action": "Waiting on employee response (asked for a screenshot, no reply yet)",
        "status": "in_progress"
    },
    {
        "id": "REQ-13",
        "employee_name": "Aman Gupta",
        "employee_email": "aman.gupta@veridian-corp.example",
        "date_opened": "Thu 24 Sep 2026",
        "request": "Laptop screen is flickering on and off, had it 2 years, might just need a fix not a replacement.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-14",
        "employee_name": "Tanya Chopra",
        "employee_email": "tanya.chopra@veridian-corp.example",
        "date_opened": "Fri 25 Sep 2026",
        "request": "Requesting approval to install a browser extension for productivity tracking.",
        "initial_action": "Not started",
        "status": "open"
    },
    {
        "id": "REQ-15",
        "employee_name": "Rahul Menon",
        "employee_email": "rahul.menon@veridian-corp.example",
        "date_opened": "Fri 25 Sep 2026",
        "request": "hey can you help, its not working",
        "initial_action": "Not started",
        "status": "open"
    }
]

EXISTING_TICKETS = [
    {
        "id": "TK-1042",
        "employee_name": "R. Verma",
        "issue_summary": "VPN credential expired",
        "status": "Resolved",
        "is_active": False,
        "resolution": "Employee renewed VPN credentials via self-service portal."
    },
    {
        "id": "TK-1043",
        "employee_name": "S. Iyer",
        "issue_summary": "Laptop replacement (3.2 yrs old)",
        "status": "Approved — pending fulfillment",
        "is_active": True,
        "resolution": None
    },
    {
        "id": "TK-1044",
        "employee_name": "A. Khan",
        "issue_summary": "Non-catalog software request",
        "status": "Pending Security review",
        "is_active": True,
        "resolution": None
    },
    {
        "id": "TK-1045",
        "employee_name": "P. Joshi",
        "issue_summary": "Mailbox quota increase",
        "status": "Approved at 35GB",
        "is_active": False,
        "resolution": "Quota increased to 35GB with manager approval."
    },
    {
        "id": "TK-1046",
        "employee_name": "M. Das",
        "issue_summary": "Printer paper jam, floor 2",
        "status": "Resolved",
        "is_active": False,
        "resolution": "Paper jam cleared and printer restarted."
    },
    {
        "id": "TK-1047",
        "employee_name": "K. Singh",
        "issue_summary": "Home office equipment request",
        "status": "Pending Finance",
        "is_active": True,
        "resolution": None
    },
    {
        "id": "TK-1048",
        "employee_name": "T. Rao",
        "issue_summary": "Phishing email reported",
        "status": "Escalated to Security — under investigation",
        "is_active": True,
        "resolution": None
    },
    {
        "id": "TK-1049",
        "employee_name": "V. Nambiar",
        "issue_summary": "Password reset",
        "status": "Resolved",
        "is_active": False,
        "resolution": "Account unlocked and password reset via IT."
    },
    {
        "id": "TK-1050",
        "employee_name": "J. Fernandes",
        "issue_summary": "Admin access request",
        "status": "Rejected — no business justification provided",
        "is_active": False,
        "resolution": "Request rejected due to lack of business justification."
    },
    {
        "id": "TK-1051",
        "employee_name": "L. Menon",
        "issue_summary": "Guest Wi-Fi issued",
        "status": "Resolved",
        "is_active": False,
        "resolution": "Guest Wi-Fi credentials generated from front-desk kiosk."
    }
]


def get_employee_request(request_id: str) -> dict | None:
    """Get a specific employee request by ID."""
    for req in EMPLOYEE_REQUESTS:
        if req["id"] == request_id:
            return req
    return None


def get_existing_ticket(ticket_id: str) -> dict | None:
    """Get a specific existing ticket by ID."""
    for ticket in EXISTING_TICKETS:
        if ticket["id"] == ticket_id:
            return ticket
    return None


def get_active_existing_tickets() -> list:
    """Get all active (non-closed) existing tickets."""
    return [t for t in EXISTING_TICKETS if t["is_active"]]


def get_open_requests() -> list:
    """Get all open employee requests."""
    return [r for r in EMPLOYEE_REQUESTS if r["status"] == "open"]


def format_requests_for_context() -> str:
    """Format all employee requests for LLM context."""
    lines = []
    for req in EMPLOYEE_REQUESTS:
        lines.append(
            f"• {req['id']} | {req['employee_name']} ({req['employee_email']}) | "
            f"{req['date_opened']} | Status: {req['status']}\n"
            f"  Request: {req['request']}\n"
            f"  Action so far: {req['initial_action']}"
        )
    return "\n\n".join(lines)


def format_tickets_for_context() -> str:
    """Format existing tickets for LLM context."""
    lines = []
    for t in EXISTING_TICKETS:
        active = "ACTIVE" if t["is_active"] else "CLOSED"
        lines.append(
            f"• {t['id']} | {t['employee_name']} | {t['issue_summary']} | "
            f"Status: {t['status']} [{active}]"
        )
    return "\n".join(lines)
