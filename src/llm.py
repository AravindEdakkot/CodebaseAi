from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from config.settings import MODEL_NAME


def load_llm():
    device = "cpu"

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True
    )

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,  # faster than float32 on 12th Gen Intel, same quality
        trust_remote_code=True
    )

    model.to(device)
    model.eval()  # disable dropout, slightly faster inference

    return tokenizer, model