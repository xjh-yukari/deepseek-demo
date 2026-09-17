import numpy as np
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from memory_embedder import Embedder
from memory_store import load_memory


CACHE_PATH = Path(__file__).resolve().parent / "memory_vectors.db"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_memory_vectors(records, embedder):
    vectors = []
    with closing(sqlite3.connect(CACHE_PATH)) as connection, connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS vectors ("
            "model TEXT, text TEXT, vector TEXT, PRIMARY KEY (model, text))"
        )
        for record in records:
            text = record["query"]
            row = connection.execute(
                "SELECT vector FROM vectors WHERE model = ? AND text = ?",
                (MODEL_NAME, text)
            ).fetchone()
            if row is None:
                vector = embedder.encode(text)
                connection.execute(
                    "INSERT INTO vectors VALUES (?, ?, ?)",
                    (MODEL_NAME, text, json.dumps(vector))
                )
            else:
                vector = json.loads(row[0])
            vectors.append(vector)
    return vectors


def clear_vector_cache():
    if CACHE_PATH.exists():
        with closing(sqlite3.connect(CACHE_PATH)) as connection, connection:
            connection.execute("DROP TABLE IF EXISTS vectors")


def retrieve_memory_context(query):
    records = load_memory()
    if not records:
        return ""

    embedder = Embedder()
    vectors = load_memory_vectors(records, embedder)
    matches = search_vectors(query, vectors, embedder, top_k=3)

    # Always retain the latest record so follow-up references have context.
    selected = [len(records) - 1]
    for score, index in matches:
        if score >= 0.55 and index not in selected:
            selected.append(index)
        if len(selected) == 3:
            break

    parts = []
    for index in sorted(selected):
        record = records[index]
        label = "最近一次" if index == len(records) - 1 else "较早记录"
        parts.append(f"[{label}] 历史问题：{record['query']}")
        for item in record["results"]:
            answer = item.get("context_answer", item["answer"])
            parts.append(f"子问题：{item['question']}\n结果：{answer}")

    print(f"记忆检索：选取 {len(selected)} / {len(records)} 条记录", flush=True)
    return "\n\n".join(parts)


def search_vectors(query, memory_vectors, embedder, top_k=3):
    if not memory_vectors or top_k <= 0:
        return []

    # 只为当前问题生成向量
    query_vector = embedder.encode(query)
    matches = []

    for index, vector in enumerate(memory_vectors):
        score = float(np.dot(query_vector, vector))
        matches.append((score, index))

    matches.sort(reverse=True)

    return matches[:top_k]


if __name__ == "__main__":
    embedder = Embedder()

    # 准备测试记忆
    memories = [
        "Python列表可以添加、删除和修改元素。",
        "元组创建后不能修改其中的元素引用。",
        "慢跑是一种有氧运动。"
    ]

    # 为记忆生成向量，供后续检索复用
    memory_vectors = []

    for text in memories:
        vector = embedder.encode(text)
        memory_vectors.append(vector)

    # 根据当前问题检索
    query = "如何给Python列表添加元素？"

    matches = search_vectors(
        query,
        memory_vectors,
        embedder,
        top_k=2
    )

    # 根据位置编号取出对应的记忆原文
    for score, index in matches:
        print(f"相似度：{score:.3f} | {memories[index]}")
