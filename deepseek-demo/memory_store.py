import json
from pathlib import Path
from unittest import result

MEMORY_PATH = Path(__file__).parent / "memory.json"

def load_memory():
    if not MEMORY_PATH.exists():
        return []

    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(query, results):
    memory = load_memory()

    record = {
        "query":query,
        "results":results
    }

    memory.append(record)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=4)

def get_memory_context():
    memory = load_memory()

    if not memory:
        return ""

    latest = memory[-1]
    parts = [f"上一问的原始内容:{latest['query']}"]

    for item in latest["results"]:
        answer = item.get("context_answer",item["answer"])
        parts.append(
            f"子问题：{item['question']}\n"
            f"结果：{answer}"
        )

    return "\n\n".join(parts)

def clear_memory():
    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump([],f)