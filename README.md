# 🏢 Veridian Corp — IT Support Agent

> **AIONOS Assignment 2 — Internal Service Agent (IT Support)**
> An intelligent, conversational IT support agent for Veridian Corp employees.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![Groq](https://img.shields.io/badge/LLM-Llama_3.3_70B-green)

## 📋 Overview

This agent handles internal employee IT support requests for Veridian Corp (set in the week of 21–25 September 2026). It uses Groq's Llama 3.3 70B model to:

- **Understand** employee issues through natural conversation
- **Find** relevant IT policies and KB articles
- **Ask** sensible follow-up questions for unclear requests
- **Resolve** simple requests directly (password resets, guest Wi-Fi, etc.)
- **Escalate** risky or unclear requests (security incidents, admin access)
- **Create** structured tickets with full audit trail
- **Show sources** — every response cites the KB article or policy used
- **Answer questions** like "What needs action today?" or "Show security incidents"

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│              Streamlit UI (app.py)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ Employee │ │ Ticket   │ │ Audit Trail  │ │
│  │ Chat     │ │Dashboard │ │ & Daily Brief│ │
│  └────┬─────┘ └────┬─────┘ └──────┬───────┘ │
│       │            │              │         │
│  ┌────▼────────────▼──────────────▼───────┐ │
│  │         Agent Core (agent_core.py)     │ │
│  │    Groq API ← Llama 3.3 70B           │ │
│  └──┬───────────────┬────────────────┬────┘ │
│     │               │                │      │
│  ┌──▼──┐    ┌───────▼──────┐  ┌──────▼────┐ │
│  │  KB  │    │ Ticket Mgr   │  │ Data Store│ │
│  │10 KB │    │ CRUD + Audit │  │ 15 REQs   │ │
│  │arts  │    │ Trail        │  │ 11 TKs    │ │
│  └──────┘    └──────────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A Groq API key (get one free at [console.groq.com](https://console.groq.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/veridian-it-agent.git
cd veridian-it-agent

# Install dependencies
pip install -r requirements.txt

# Set your API key (Option 1: environment variable)
export GROQ_API_KEY="your_key_here"       # Linux/Mac
set GROQ_API_KEY=your_key_here             # Windows CMD
$env:GROQ_API_KEY="your_key_here"          # Windows PowerShell

# Run the app
streamlit run app.py
```

Alternatively, you can enter the API key directly in the app's sidebar.

## Features (4 Focused Views)

### 1. Employee Chat
Main interactive conversational agent interface:
- Chat as any employee from the data pack (REQ-01 to REQ-15) or test custom scenarios
- Identifies the issue and grounds resolution strictly in KB articles
- Detects policy conflicts (e.g., 3-year laptop eligibility in KB-03 vs 4-year cycle in Asset Management Policy)
- Asks sensible follow-up questions for ambiguous requests (e.g. REQ-15)
- Automatically escalates security incidents (KB-09) and unverified admin access requests
- Generates structured tickets inline and maintains session audit trails

### 2. Requests & Tickets
Single unified review page for all data pack requests:
- Process individual employee requests or 1-click batch process all 15 requests
- Inline structured ticket card displayed directly under each request with Ticket ID, Category, Priority, Status, Assigned To, Source KB, and Notes
- Collapsible historical ticketing system queue (TK-1042 to TK-1051) for precedent reference

### 3. Audit Trail
Comprehensive regulatory and compliance log:
- Full timestamped log of all agent decisions and lifecycle events
- Records exact action, ticket reference, governing KB source, and decision rationale
- Filter by action type (TICKET_CREATED, TICKET_ESCALATED, CHAT_INTERACTION, etc.)
- One-click JSON export for audit compliance

### 4. Knowledge Base & Policies
Policy grounding reference:
- All 10 Knowledge Base articles (KB-01 to KB-10) with categories and approval constraints
- Full extract of Finance & Assets Asset Management Policy (Q2 2026)

## 📦 Data Sources

All data is sourced from the assignment data pack:
- **10 Knowledge Base articles** (KB-01 to KB-10) — IT policies and procedures
- **Asset Management Policy** — 4-year hardware refresh cycle
- **15 Employee Requests** (REQ-01 to REQ-15) — the week's IT issues
- **11 Existing Tickets** (TK-1042 to TK-1051) — historical ticket context

## 🛠️ AI Tools Used

| Tool | Usage |
|------|-------|
| **Groq API** | LLM inference (Llama 3.3 70B Versatile) for issue classification, response generation, and Q&A |
| **Streamlit** | Interactive web UI framework |
| **Google Antigravity** | AI-assisted code generation and development |

## 📁 Project Structure

```
veridian-it-agent/
├── app.py              # Streamlit UI — main entry point
├── agent_core.py       # LLM agent with Groq API integration
├── knowledge_base.py   # KB articles (KB-01–KB-10) + Asset Policy
├── ticket_manager.py   # Ticket CRUD + audit trail
├── data_store.py       # Employee requests + existing tickets
├── config.py           # System prompts + configuration
├── requirements.txt    # Python dependencies
├── .env.example        # API key template
└── README.md           # This file
```

## 📄 License

This project was created as part of the AIONOS recruitment assignment.
