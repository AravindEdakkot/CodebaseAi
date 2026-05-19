import re
import torch
from config.settings import (
    SUMMARY_FETCH_DOCS, SUMMARY_TOP_DOCS, QA_TOP_DOCS,
    MAX_NEW_TOKENS_QA, MAX_NEW_TOKENS_SUMMARY,
    CONTEXT_CHARS_QA, CONTEXT_CHARS_SUMMARY
)


def classify_query(query):
    q = query.lower()
    if any(k in q for k in ["api", "backend", "server", "endpoint"]):
        return "backend"
    if any(k in q for k in ["ui", "frontend", "html", "css"]):
        return "frontend"
    return "general"


def expand_query(query):
    q = query.lower()
    extra = []
    if any(w in q for w in ["how", "process", "work", "flow"]):
        extra.extend(["function", "implementation", "logic", "data flow", "model", "training", "prediction"])
    return query + " " + " ".join(extra)


def is_junk(content):
    junk_patterns = ["question", "example usage", "write a python function",
                     "stack overflow", "tutorial", "<|", "|>"]
    return any(p in content.lower() for p in junk_patterns)


def score_chunk(content):
    score = 0
    if "def " in content: score += 2
    if "class " in content: score += 2
    if "return" in content: score += 1
    if "(" in content: score += 1
    return score


def ask_question(query, retriever, tokenizer, model):
    query_lower = query.lower()

    is_summary = any(k in query_lower for k in [
        "summary", "architecture", "overview", "explain repository"
    ])

    # Step 1: Retrieve
    expanded = expand_query(query)
    raw_docs = retriever.invoke(query if is_summary else expanded)

    # Step 2: Deduplicate + filter junk
    seen, clean_docs = set(), []
    for d in raw_docs:
        if d.page_content not in seen and not is_junk(d.page_content):
            clean_docs.append(d)
            seen.add(d.page_content)

    # Step 3: Score and trim (use constants, not magic numbers)
    if is_summary:
        top_docs = clean_docs[:SUMMARY_TOP_DOCS]
    else:
        scored = sorted(clean_docs, key=lambda d: score_chunk(d.page_content), reverse=True)
        top_docs = scored[:QA_TOP_DOCS]

    # Step 4: Build context
    char_limit = CONTEXT_CHARS_SUMMARY if is_summary else CONTEXT_CHARS_QA
    context_parts = []
    for d in top_docs:
        source = d.metadata.get("source", "unknown file")
        context_parts.append(f"# File: {source}\n{d.page_content.strip()[:char_limit]}")

    context = "\n\n".join(context_parts)

    # Step 5: Prompt
    if is_summary:
        prompt = f"""You are a senior software engineer.

Explain this repository as a SYSTEM (not file-by-file).

Structure:
- Overview (what the project does)
- Components (group related logic, not just files)
- Workflow (step-by-step pipeline)
- Key Features
- Limitations

Rules:
- Do NOT list files one by one
- Combine related functionality into components
- Focus on system design

Code:
{context}

Answer:
"""
    else:
        prompt = f"""You are a code analysis assistant. Answer using ONLY the given code.

Code:
{context}

Question: {query}

Instructions:
- Be precise
- Reference functions/files when needed
- If not found, say "Not found in the provided code"

Answer:
"""

    # Step 6: Generate inside inference_mode (no grad tracking = faster + less memory)
    inputs = tokenizer(prompt, return_tensors="pt")
    max_tokens = MAX_NEW_TOKENS_SUMMARY if is_summary else MAX_NEW_TOKENS_QA

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    answer = response.split("Answer:")[-1].strip()
    answer = re.sub(r"<\|.*?\|>", "", answer)

    # Step 7: Deduplicate lines
    lines, seen_lines = [], set()
    for line in answer.split("\n"):
        line = line.strip()
        if line and line not in seen_lines:
            lines.append(line)
            seen_lines.add(line)

    return "\n".join(lines)