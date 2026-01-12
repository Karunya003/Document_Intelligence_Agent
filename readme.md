# 📄 Document Intelligence Agent

## Overview
This repository contains a **production-ready Document Intelligence Agent** built as part of a 24 hr technical assignment. The system ingests unstructured PDF documents and immediately produces a **structured insight** while also supporting **conversational Q&A** over the uploaded document.

The solution is designed with  **tool-based orchestration** and a **chat-based user interface** suitable for real-world enterprise use cases.

## 🎥 Demo Video

▶️ [Click to watch the demo]([Demo.mp4](https://github.com/user-attachments/assets/bfb145c8-13cc-43b1-9cda-87e552e9b9a6))

---

## Assignment Objectives

The goals of this assignment were interpreted as:

- Ingest long, unstructured documents (PDFs)
- Extract structured insights automatically on upload
- Support follow-up natural language questions
- Ensure modular, extensible, production-quality design
- Clearly separate ingestion, reasoning, retrieval, and UI layers

---

## Key Features

- 📥 **PDF Upload & Parsing** (PyPDF)
- 🧠 **LLM-powered Agent**  (ReAct Agent)
- 🧰 **Tool-based reasoning** (summary, entities, risks, metrics, Q&A)
- 💬 **Conversational Chat Interface** (Streamlit)
- ⚙️ **FastAPI backend** (optional API mode)

---

## System Architecture

```
User
   ↓
FastAPI Endpoint / Chat UI
   ↓
Agent Executor
   ├─> [PDF Extractor Tool]  → Extracts raw text from uploaded PDF
   └─> [Other Dynamic Tools] → Performs analysis, metrics extraction
   ↓
LLM (OpenAI) → Process and format results 
   ↓
<<<<<<< HEAD
Structured Response
   ↓
FastAPI Endpoint / Chat UI
=======
Structured JSON Response
   ↓
FastAPI Endpoint / Chat UI

>>>>>>> c6616a2c1d4df7f3036c67a262d70ffc55a28102
```

---

## Output Schema

On document upload, the system generates a structured output using chat UI:

 "summary": "...",
  "key_entities": [],
  "risks": [],
  "metrics": []

This output is generated **immediately after ingestion**, before any follow-up questions are asked.

---

## Conversational Capabilities

After ingestion, the agent behaves as a **stateful conversational assistant**:

- Uses conversation memory (`chat_history`)
- Selects tools dynamically based on user questions
- Avoids hallucination by grounding answers in document chunks

---

## Project Structure

```
Document_Intelligence_Agent/
│
├── agent/
│   ├── agent.py        # Agent construction
│   ├── tools.py        # Document tools (summary, QA, extraction)
│   ├── prompts.py      # ReAct prompt
│   ├── schemas.py      # Output schemas
│
├── api/
│   └── main.py         # FastAPI backend
│
├── data/
│   ├── uploads/        # Ignored (runtime only)
│   
│
├── app.py    # Conversational Streamlit UI
├── requirements.txt
├── .env.example
└── README.md
```

---

## Assumptions Made

The following assumptions were made while completing this assignment:

1. **Single-document context**
   - Each session focuses on one uploaded PDF at a time.

2. **Read-only documents**
   - Documents are not modified or annotated; only analyzed.

3.  **LLM access available**
   - A valid OpenAI-compatible API key is assumed at runtime.

4. **Latency > cost optimization**
   - Design favors clarity, accuracy, and traceability over minimal token usage.

5. **Security scope**
   - Authentication and authorization are considered out-of-scope for this assignment.

---

## How to Run

```bash
# 1. Create virtual environment
python -m venv venv
Mac: source venv/bin/activate (or)
Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Add your API key

# 4. Run FastAPI app
unicorn api.main:app --reload

# 5. Run Streamlit app
streamlit run app.py
```

---

## Why This Design

- **Agent-based approach** enables extensibility
- **Tool separation** mirrors real production systems
- **Conversational UI** reflects real user workflows

This architecture is intentionally aligned with **enterprise document intelligence systems** rather than a simple demo pipeline.

---

## Notes for Reviewers

- The system is designed to scale to additional tools (compliance checks, sentiment analysis, cross-doc comparison).
- The FastAPI backend can be used instead of Streamlit for service-based deployment.
- All secrets and runtime data are excluded from version control.

---

## Author

**Karunya Srinivasan**  
MSc Computer Science  
AI / Data / ML Engineer Candidate

