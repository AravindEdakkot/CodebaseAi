# 💻 CodebaseAI — Chat With Any Codebase

> Ask questions about any code repository using a **local LLM** — no API keys, no internet required after setup.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-red)
![LLM](https://img.shields.io/badge/LLM-Qwen2.5--Coder-green)
![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-orange)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 What is this?

**CodebaseAI** is a RAG (Retrieval-Augmented Generation) tool that lets you load any GitHub repository or local folder and ask natural language questions about the code. It runs entirely on your machine using open-source models.

---

## 🧠 How It Works

```
Your Question
     │
     ▼
Embedding Model (BAAI/bge-base-en-v1.5)
     │  converts question to vector
     ▼
FAISS Vector Store
     │  finds most relevant code chunks
     ▼
Hybrid Retriever (FAISS + BM25)
     │  ranks and filters results
     ▼
LLM (Qwen2.5-Coder-7B-Instruct)
     │  reads chunks + generates answer
     ▼
Answer displayed in Streamlit UI
```

### Pipeline Steps

| Step | What Happens |
|------|-------------|
| **Load** | Clones GitHub repo or reads local folder |
| **Split** | Breaks code into meaningful chunks (functions, classes) |
| **Embed** | Converts chunks to vectors using `bge-base-en-v1.5` |
| **Index** | Stores vectors in FAISS (cached to disk per repo) |
| **Retrieve** | Hybrid search — semantic (FAISS) + keyword (BM25) |
| **Generate** | LLM reads retrieved chunks and writes the answer |

---

## ✨ Features

- 🔒 **Fully offline** — no OpenAI or external API needed
- 🐙 **GitHub support** — paste any public repo URL to auto-clone
- ⚡ **FAISS caching** — index is saved per repo, not rebuilt every time
- 🔍 **Hybrid retrieval** — combines semantic search + BM25 keyword search
- 📋 **Repo summary mode** — generates a structured architectural overview
- 💬 **Chat history** — all Q&A displayed in session
- 📁 **File tree viewer** — browse loaded repo structure in the sidebar

---

## 🗂️ Project Structure

```
CodebaseAI/
├── app.py                  # Streamlit UI and app logic
├── config/
│   └── settings.py         # All model and retrieval settings
├── src/
│   ├── loader.py           # GitHub cloning and file loading
│   ├── splitter.py         # Code chunking (function/class aware)
│   ├── embeddings.py       # FAISS index + hybrid retriever
│   ├── llm.py              # Model loading (Qwen)
│   └── qa.py               # Retrieval, prompting, generation
├── faiss_index/            # Cached FAISS indexes (auto-created)
├── repos/                  # Cloned repositories (auto-created)
└── requirements.txt
```

---

## ⚙️ Supported File Types

`.py` `.js` `.ts` `.java` `.cpp` `.html` `.css` `.json` `.md`

---

## 🚀 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/CodebaseAI.git
cd CodebaseAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🖥️ Usage

1. Open the app in your browser (usually `http://localhost:8501`)
2. In the **sidebar**, enter a GitHub URL or local folder path
3. Click **🚀 Load Codebase** — wait for indexing to complete
4. Click **Generate Summary** for a high-level architectural overview
5. Type any question in the chat box and click **Ask**

### Example Questions

```
What does this project do?
Which libraries are used in scraper.py?
How does the sentiment analysis work?
What is the main entry point of this app?
Explain the retrieval pipeline
```

---

## 🔧 Configuration

All settings live in `config/settings.py`. You can tune them without touching any logic:

```python
# Model
MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"   # change model here
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# Retrieval
TOP_K = 4                  # chunks fetched per query
SUMMARY_TOP_DOCS = 8       # chunks used in summary mode
QA_TOP_DOCS = 5            # chunks used in Q&A mode

# Generation
MAX_NEW_TOKENS_QA = 300
MAX_NEW_TOKENS_SUMMARY = 400

# Context window (characters per chunk)
CONTEXT_CHARS_QA = 2000
CONTEXT_CHARS_SUMMARY = 3000
```

---

## 💻 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 8 GB | 16 GB |
| CPU | Any modern x86 | Intel 12th Gen+ |
| GPU | Not required | Optional (CUDA) |
| Storage | 5 GB free | 10 GB free |

### Expected Response Times (CPU only, 16GB RAM)

| Task | 1.5B Model | 7B Model |
|------|-----------|---------|
| Model load (first time) | ~30–45 sec | ~2–3 min |
| Repo indexing | ~1–2 min | ~1–2 min |
| Per question | ~3–5 min | ~8–12 min |
| Summary generation | ~4–6 min | ~10–15 min |

> 💡 The FAISS index and model are cached after first load — subsequent questions in the same session skip the loading step.

---

## 📦 Dependencies

```
streamlit
transformers
torch
sentence-transformers
langchain
langchain-community
langchain-core
faiss-cpu
rank-bm25
gitpython
textblob
```

---

## 🛠️ Known Limitations

- **CPU only** — responses are slow without a GPU
- **Context window** — very large repos may have incomplete coverage
- **Hallucination** — smaller models (1.5B) may generate inaccurate answers; use 7B for better quality
- **English only** — prompts and expected answers are in English
- **Public repos only** — private GitHub repos require authentication setup

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first.

---

## 📄 License

MIT License — free to use, modify, and distribute.
