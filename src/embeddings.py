import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from config.settings import EMBEDDING_MODEL, TOP_K

FAISS_INDEX_PATH = "faiss_index"


# 🔹 Embedding model
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        cache_folder=".embedding_cache",
        model_kwargs={"device": "cpu"},  # ✅ stable (no GPU issues)
        encode_kwargs={"normalize_embeddings": True}  # ✅ better similarity
    )


# 🔹 Create / Load FAISS index
def create_vector_store(docs, repo_name: str):
    if not docs:
        raise ValueError("❌ No documents found. Check your input pipeline.")

    index_path = f"{FAISS_INDEX_PATH}/{repo_name}"
    embeddings = get_embeddings()

    if os.path.exists(index_path):
        print(f"✅ Loading existing FAISS index for '{repo_name}'...")
        db = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print(f"🔨 Building FAISS index for '{repo_name}'...")
        db = FAISS.from_documents(docs, embeddings)
        os.makedirs(index_path, exist_ok=True)
        db.save_local(index_path)

    return db


# 🔹 Hybrid Retriever (Vector + BM25)
def get_retriever(db, docs):
    # ✅ Better retrieval (MMR = diverse + relevant)
    vector_retriever = db.as_retriever(
        search_type="mmr",
        search_kwargs={"k": TOP_K, "fetch_k": 50}
    )

    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = TOP_K

    class SimpleEnsembleRetriever:
        def invoke(self, query):
            vector_docs = vector_retriever.invoke(query)
            bm25_docs = bm25_retriever.invoke(query)

            # 🔥 prioritize vector results, reduce BM25 noise
            combined_raw = vector_docs + bm25_docs[: max(1, TOP_K // 2)]

            normalized = []
            seen = set()

            for doc in combined_raw:
                # 🔹 Normalize dict / Document
                if isinstance(doc, dict):
                    content = doc.get("page_content") or doc.get("content") or str(doc)
                    metadata = doc.get("metadata", {})
                else:
                    content = getattr(doc, "page_content", str(doc))
                    metadata = getattr(doc, "metadata", {})

                # 🔹 Skip weak chunks
                if not content or len(content) < 100:
                    continue

                # 🔹 Deduplicate
                if content in seen:
                    continue
                seen.add(content)

                # 🔹 Use proper Document (no dynamic class hack)
                normalized.append(
                    Document(
                        page_content=content,
                        metadata=metadata
                    )
                )

            return normalized[:TOP_K]

    return SimpleEnsembleRetriever()