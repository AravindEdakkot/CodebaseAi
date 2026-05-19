import re
from langchain_core.documents import Document
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP


# 🔹 Detect functions & classes (Python-focused but works broadly)
def extract_code_blocks(code):
    pattern = r"(def\s+\w+\(.*?\):|class\s+\w+\(?.*?\)?:)"
    matches = list(re.finditer(pattern, code))

    blocks = []

    if not matches:
        return [code]

    for i, match in enumerate(matches):
        start = match.start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(code)

        block = code[start:end].strip()
        if len(block) > 50:
            blocks.append(block)

    return blocks


# 🔹 Fallback: smart chunking
def fallback_chunk(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


# 🔹 MAIN SPLITTER
def split_code(code_list):
    docs = []

    for file in code_list:
        content = file["content"]
        metadata = {
            "source": file["path"],
            "filename": file["filename"],
            "ext": file["ext"]
        }

        # 🔥 Step 1: Extract functions/classes
        blocks = extract_code_blocks(content)

        # 🔥 Step 2: If no structure → fallback
        if len(blocks) <= 1:
            blocks = fallback_chunk(content, CHUNK_SIZE, CHUNK_OVERLAP)

        # 🔥 Step 3: Create documents
        for block in blocks:
            docs.append(
                Document(
                    page_content=block.strip(),
                    metadata=metadata
                )
            )

    return docs