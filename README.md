#  Personal AI Assistant

A complete AI-powered personal assistant built with 
LangChain, RAG, Groq, SQLite and Streamlit.

##  Live Demo
[Click here to try it live](https://personal-ai-assistant-739ngzcmjz4j7ne8iqzjmu.streamlit.app/)

##  Features
-  **Chat with AI** — Intelligent conversations with memory
-  **Document Q&A** — Upload PDFs, ask questions with page citations
-  **Email Assistant** — AI drafts professional emails automatically  
-  **Task Manager** — Add, complete and delete tasks with SQLite
  ## Upcoming Features
- **Expense Tracker** — Track your monthly expenses

##  Tech Stack
- **LangChain** — AI framework for RAG pipeline
- **Groq API** — Fast LLM inference (Llama3)
- **ChromaDB** — Vector database for document storage
- **HuggingFace** — Free embeddings (all-MiniLM-L6-v2)
- **SQLite** — Local database for tasks
- **Streamlit** — Web interface
- **Python** — Core language

##  Architecture
User Question → Embed Question → Search ChromaDB
→ Find Similar Chunks → Build Prompt → Groq LLM
→ Answer with Citations → Zero Hallucination

## 📁 Project Structure
personal-ai-assistant/
├── final_app.py        # Main Streamlit application
├── rag_system.py       # RAG pipeline with ChromaDB
├── todo_manager.py     # SQLite task management
├── email_assistant.py  # AI email drafting
├── memory.py           # Conversation memory
└── requirements.txt    # Dependencies

## How to Run Locally
```bash
pip install -r requirements.txt
streamlit run final_app.py
```

##  Built By
**Stephen David** | AI & Data Science | Hyderabad  
Investment Banking professional transitioning to AI/ML  
Target: Data Scientist role in BFSI/Fintech

---
*Built as part of AI & Data Science portfolio — June 2026*

