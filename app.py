import streamlit as st
from src.loader import load_codebase
from src.splitter import split_code
from src.embeddings import create_vector_store, get_retriever
from src.llm import load_llm
from src.qa import ask_question
import os

st.set_page_config(page_title="CodebaseAI", layout="wide")

st.title("💻 CodebaseAI — Codebase Q&A")

# -----------------------------
# 🔥 CACHED FUNCTIONS
# -----------------------------

@st.cache_resource
def get_llm_cached():
    return load_llm()

@st.cache_data
def process_codebase_cached(folder):
    code_files, repo_name = load_codebase(folder)
    docs = split_code(code_files)
    return code_files, docs, repo_name

@st.cache_resource
def build_retriever_cached(docs, repo_name):
    db = create_vector_store(docs, repo_name)
    retriever = get_retriever(db, docs)
    return retriever


# -----------------------------
# 📂 SIDEBAR
# -----------------------------

st.sidebar.title("⚙️ Controls")

folder = st.sidebar.text_input("📁 Repo URL / Path")

if st.sidebar.button("🚀 Load Codebase"):
    if not folder.strip():
        st.sidebar.warning("Enter repo path")
    else:
        with st.spinner("Loading and indexing..."):
            try:
                code_files, docs, repo_name = process_codebase_cached(folder)
                retriever = build_retriever_cached(docs, repo_name)

                st.session_state["retriever"] = retriever
                st.session_state["repo_name"] = repo_name
                st.session_state["code_files"] = code_files
                st.session_state["summary"] = None   # reset summary

                st.sidebar.success(f"✅ {repo_name} loaded")

            except Exception as e:
                st.sidebar.error(f"❌ {e}")



# -----------------------------
# 📁 FILE STRUCTURE (SIDEBAR)
# -----------------------------

st.sidebar.markdown("### 📁 File Structure")

if "code_files" in st.session_state:

    file_paths = [f["path"] for f in st.session_state["code_files"]]

    tree = {}
    for path in file_paths:
        parts = path.split(os.sep)
        current = tree
        for p in parts:
            current = current.setdefault(p, {})

    def display_tree_sidebar(container, d, indent=0):
        for key, value in d.items():
            container.text("   " * indent + "📄 " + key)
            if isinstance(value, dict):
                display_tree_sidebar(container, value, indent + 1)

    with st.sidebar.expander("View Files", expanded=False) as exp:
        display_tree_sidebar(exp, tree)

else:
    st.sidebar.caption("Load repo to see structure")

# -----------------------------
# 🧾 REPO SUMMARY
# -----------------------------

st.subheader("📌 Repository Summary")

if "retriever" in st.session_state:

    if st.button("Generate Summary"):
        with st.spinner("Analyzing repo..."):
            try:
                tokenizer, model = get_llm_cached()

                summary = ask_question(
                    """SUMMARY_MODE: Explain this repository in a structured and presentation-ready format.

Include:
1. Project purpose
2. Main components (group logically, not file-by-file)
3. Workflow (step-by-step)
4. Key features
5. Limitations

Rules:
- DO NOT list files blindly
- Focus on system-level understanding
- Use clear sections and bullet points
""",
                    st.session_state["retriever"],
                    tokenizer,
                    model
                )

                st.session_state["summary"] = summary

            except Exception as e:
                st.error(f"❌ Summary error: {e}")

# Display summary
if "summary" in st.session_state and st.session_state["summary"]:
    with st.expander("📌 View Repository Summary", expanded=True):
        st.markdown(st.session_state["summary"])
else:
    st.caption("Click 'Generate Summary' to analyze the repo")


# -----------------------------
# 💬 CHAT
# -----------------------------

st.subheader("💬 Ask Questions")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("Type your question")

col1, col2 = st.columns([1, 1])

with col1:
    ask_btn = st.button("Ask")

with col2:
    clear_btn = st.button("Clear Chat")

if clear_btn:
    st.session_state.chat_history = []

if ask_btn:
    if "retriever" not in st.session_state:
        st.warning("Load a codebase first")
    elif not query.strip():
        st.warning("Enter a question")
    else:
        with st.spinner("Thinking..."):
            try:
                tokenizer, model = get_llm_cached()

                answer = ask_question(
                    query,
                    st.session_state["retriever"],
                    tokenizer,
                    model
                )

                st.session_state.chat_history.append({
                    "q": query,
                    "a": answer
                })

            except Exception as e:
                st.error(f"❌ {e}")


# -----------------------------
# 📜 CHAT DISPLAY
# -----------------------------

for chat in reversed(st.session_state.chat_history):
    st.markdown("### 🧑 Question")
    st.markdown(chat["q"])

    st.markdown("### 🤖 Answer")
    st.markdown(chat["a"])

    st.markdown("---")