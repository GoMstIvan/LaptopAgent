import os
import json
import numpy as np
import requests
import time
import platform
import subprocess
import sys
from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity

from conversation_handler import ConversationHandler

# === 設定 ===
OLLAMA_URL = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_URL}/api/chat"
OLLAMA_EMBED_URL = f"{OLLAMA_URL}/api/embeddings"
EMBED_MODEL = "shaw/dmeta-embedding-zh"
GRAPH_PATH = "rag/graph.json"


# === 載入圖資料與執行 GraphRAG 查詢 ===
def load_graph_data() -> Dict:
    with open(GRAPH_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_query_embedding(query: str) -> List[float]:
    response = requests.post(OLLAMA_EMBED_URL, json={
        "model": EMBED_MODEL,
        "prompt": query
    })
    response.raise_for_status()
    return response.json()["embedding"]


def graph_rag_retrieve(query: str, top_k=5) -> List[Dict]:
    graph = load_graph_data()
    nodes = graph["nodes"]
    embeddings = []

    for node in nodes:
        desc = node["description"]
        response = requests.post(OLLAMA_EMBED_URL, json={
            "model": EMBED_MODEL,
            "prompt": desc
        })
        response.raise_for_status()
        node_embedding = response.json()["embedding"]
        embeddings.append({
            "node": node,
            "embedding": node_embedding
        })

    query_embedding = np.array(get_query_embedding(query))
    matrix = np.array([np.array(e["embedding"]) for e in embeddings])
    similarities = cosine_similarity([query_embedding], matrix)[0]

    ranked = sorted(zip(embeddings, similarities), key=lambda x: x[1], reverse=True)
    return [dict(node=item[0]["node"], score=item[1]) for item in ranked[:top_k]]


# === 對話控制器 ===
class ConversationController:
    def __init__(self, model="qwen2.5:3b"):
        self.model = model
        self.conversation_handler = ConversationHandler()
        self.conversation_id = self.conversation_handler.new_conversation(model)
        print(f"🆕 Started new conversation with ID: {self.conversation_id}")

    def chat_with_llm(self, user_input: str):
        self.conversation_handler.add_message("user", user_input)

        # 🔍 GraphRAG 檢索最相關的公司節點描述
        context_entries = graph_rag_retrieve(user_input, top_k=5)
        context_text = "\n\n".join([
            f"[{item['node']['id']}]: {item['node']['description']}"
            for item in context_entries
        ])

        # 準備 messages 結構（加入系統提示 + 檢索補充）
        messages = [
            {"role": "system", "content": "你是一位對科技產業公司熟悉的助手，請根據以下公司資訊與對話歷史回覆問題。\n\n" + context_text}
        ]
        messages += [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_handler.get_conversation_history()
        ]

        try:
            response = requests.post(
                OLLAMA_CHAT_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": self.model,
                    "messages": messages,
                    "stream": True
                }),
                stream=True
            )

            if response.status_code != 200:
                print(f"\n❌ Failed to get response: {response.status_code}")
                print(response.text)
                return

            print("\nAssistant: ", end="", flush=True)
            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            print()
            self.conversation_handler.add_message("assistant", full_response)

        except Exception as e:
            print(f"\n❌ Error communicating with Ollama: {e}")


# === 主程式 ===
if __name__ == "__main__":
    ctrl = ConversationController(model="qwen2.5:3b")

    print("\n✅ GraphRAG 模式啟動：直接輸入問題開始對話")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input:
                ctrl.chat_with_llm(user_input)
        except KeyboardInterrupt:
            print("\n🛑 KeyboardInterrupt detected")
            ctrl.conversation_handler.save_conversation()
            break
