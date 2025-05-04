import os
import json
import numpy as np
import requests
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict

OLLAMA_URL = "http://localhost:11434/api/embeddings"
OLLAMA_MODEL = "shaw/dmeta-embedding-zh"
EMBEDDING_PATH = "rag/embeddings.json"

# === 載入 Embedding ===
def load_rag_embeddings(path: str = EMBEDDING_PATH) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# === 查詢向量 ===
def get_query_embedding(query: str, model: str = OLLAMA_MODEL) -> List[float]:
    response = requests.post(OLLAMA_URL, json={
        "model": model,
        "prompt": query
    })
    response.raise_for_status()
    return response.json()["embedding"]

# === Top-K 相似搜尋 ===
def search_top_k(query: str, embeddings: List[Dict], top_k=5) -> List[Dict]:
    query_vec = np.array(get_query_embedding(query))
    all_vecs = np.array([e["embedding"] for e in embeddings])
    scores = cosine_similarity([query_vec], all_vecs)[0]

    ranked = sorted(zip(embeddings, scores), key=lambda x: x[1], reverse=True)
    return [dict(item[0], score=item[1]) for item in ranked[:top_k]]

# === 範例執行 ===
if __name__ == "__main__":
    embeddings_data = load_rag_embeddings()
    question = "哪間廠商同時有相機與感測器？"
    top_matches = search_top_k(question, embeddings_data)

    print(f"\n🔍 查詢：「{question}」\n")
    for i, match in enumerate(top_matches, 1):
        print(f"#{i} 📝 {match['source']} ({match['score']:.3f})")
        print(f"{match['text']}\n")
