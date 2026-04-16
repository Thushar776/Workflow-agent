# Workflow Automation Agent 🚀

An AI-driven workflow automation platform that handles Gmail, Google Calendar, and CSV data analysis via natural language.

## 📝 Problem Statement
Modern professionals are overwhelmed by juggling multiple SaaS tools (Email, Calendar, Spreadsheets). Manually extracting data or scheduling events across these platforms is time-consuming and error-prone. There is a need for a unified "Agentic" interface that understands intent and executes actions autonomously.

## ✨ Proposed Solution
The **Workflow Automation Agent** provides a centralized Chat interface where users can issue high-level instructions:
- *"Read my emails and summarize the urgent ones."*
- *"Schedule a meeting with the team for tomorrow at 3 PM."*
- *"Analyze this sales CSV and tell me which region performed best."*

The system utilizes LLM function-calling to map intent to specific tool executions, ensuring a seamless and productive experience.

## 🛠️ Tech Stack
- **Frontend**: React (Vite), Vanilla CSS (Modern Dark/Blocky UI)
- **Backend**: Python FastAPI, SQLAlchemy (MVC Architecture)
- **AI Engine**: OpenAI GPT-4o-mini (Advanced Function Calling)
- **Queue/Worker**: Redis & Python Background Workers (Scalable Task Processing)
- **Database**: SQLite (Development)
- **Security**: AES-256 PII Encryption (Fernet), MFA (OTP-based)
- **Observability**: Grafana, Loki, Promtail (Structured Tracing)

## 📸 Screenshots
*(Coming Soon - Place your captured UI screenshots here)*

## 🚀 How to Run

### Option 1: Full Stack (Docker Swarm - Recommended)
The entire ecosystem (Frontend, API, Redis, Workers, Logging) is dockerized and can be launched with a single command:
```bash
docker-compose up -d --build
```
- **Web App**: `http://localhost:80`
- **API Docs**: `http://localhost:8000/docs`
- **Grafana (Logs)**: `http://localhost:3000`

### Option 2: Local Development
1. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## 🛡️ Hackathon Special Features
- **MFA Login**: Secure 2-factor authentication on every login.
- **Atomic Scaling**: Multi-worker parallelisation for heavy AI tasks.
- **PII Encryption**: User data is never stored in plain text.
- **Observability**: Full trace-ID logging linked to Grafana.
