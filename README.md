# Context-Aware Conversational Agent
A full-stack, context-aware chatbot system built with LangGraph, FastAPI, and Next.js that can answer queries from uploaded documents and guide users through appointment booking — all within a single conversational interface.

---

## Features

- **Document Query (RAG)** — Upload documents in `.txt`, `.pdf`, or `.md` format and ask questions against them. Responses are generated using retrieval-augmented generation with PGVector for semantic search and Ollama as the local LLM.
- **Appointment Booking** — A conversational form that collects and validates user details (name, phone, email, preferred date) with natural language date parsing (e.g. "Next Monday" → `YYYY-MM-DD`).
- **Context Switching** — Seamlessly switch between document queries and appointment booking within the same session.
- **Persistent Memory** — Conversation history is stored in PostgreSQL, enabling context-aware responses across turns.
- **Local LLM** — Fully local inference using Ollama for both chat and embeddings — no external API calls required.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js |
| Backend | FastAPI |
| Agent Orchestration | LangGraph |
| LLM & Embeddings | Ollama (local) |
| Vector Store | PGVector (PostgreSQL) |
| Persistent Memory | PostgreSQL |

---

## LangGraph Agent Flow

Every incoming message passes through `intent_classification`, which routes it to the appropriate handler node:

| Intent | Handler | Description |
|---|---|---|
| `appointment` | `AP` node | Guides user through booking form with validation |
| `casual_conversation` | `CC` node | General chat responses via Ollama |
| `knowledge_base` | `KBQ` node | RAG-based document query |
| `low_confidence` | `LC` node | Asks user to clarify their intent |
| `other` | `OT` node | Fallback response |

---

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [Python](https://www.python.org/) 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- [PostgreSQL](https://www.postgresql.org/) with PGVector extension

### 1. Clone the repository

```bash
git clone https://github.com/basantbhandari/agentic_chatbot_langgraph.git
cd agentic_chatbot_langgraph
```

### 2. Set up Ollama models

```bash
ollama pull llama3            # or your preferred chat model
ollama pull nomic-embed-text  # embedding model
```

### 3. Set up PostgreSQL with PGVector

```bash
docker-compose up -d
```

Or manually enable PGVector in your Postgres instance:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Backend setup

```bash
cd backend
uv venv
source .venv/bin/activate
uv sync
```

Run the backend:

```bash
uvicorn main:app --reload --port 8000
```

### 5. Frontend setup

```bash
cd frontend
npm install
```

Run the frontend:

```bash
npm run dev
```

Visit `http://localhost:3000`

---

## Usage

### Document Queries

1. Navigate to the **Knowledge Base** section
2. Upload a `.txt`, `.pdf`, or `.md` file
3. Return to the chat and ask questions about the document
4. To reset, clean the knowledge base and re-upload a new document

### Appointment Booking

Start a conversation with something like:

> "I'd like to book an appointment"

The agent will guide you through:

- **Name** — validated as non-empty
- **Phone number** — validated for correct length and numeric format
- **Email** — validated against standard email pattern
- **Preferred date** — accepts natural language (e.g. "next Monday", "in two days", "coming Tuesday") and converts to `YYYY-MM-DD`

## License

This project is licensed under the MIT License.
