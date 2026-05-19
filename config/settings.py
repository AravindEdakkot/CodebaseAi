MODEL_NAME = "Qwen/Qwen2.5-Coder-7B-Instruct"
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

# Chunking
CHUNK_SIZE = 2500
CHUNK_OVERLAP = 250

# Retrieval
TOP_K = 4
SUMMARY_FETCH_DOCS = 10       # how many docs to retrieve in summary mode
SUMMARY_TOP_DOCS = 8          # how many to keep after scoring in summary mode
QA_TOP_DOCS = 5               # how many to keep after scoring in QA mode

# Generation
MAX_NEW_TOKENS_QA = 300       # reduced from 400 for speed
MAX_NEW_TOKENS_SUMMARY = 400  # reduced from 500 for speed

# Context window per chunk (characters)
CONTEXT_CHARS_QA = 2000
CONTEXT_CHARS_SUMMARY = 3000