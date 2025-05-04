import os
import json
import requests
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm  # ✅ 加入 tqdm 進度條套件

DATA_DIR = Path("rag/data")
OUTPUT_PATH = Path("rag/embeddings.json")
OLLAMA_MODEL = "shaw/dmeta-embedding-zh"
OLLAMA_URL = "http://localhost:11434/api/embeddings"

def split_into_paragraphs(text: str) -> List[str]:
    """將文件按段落切分"""
    return [p.strip() for p in text.split("\n") if p.strip()]

def load_documents(data_dir: Path) -> List[Dict]:
    """讀取所有 .md 文件並切分段落"""
    documents = []
    for file in data_dir.glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        paragraphs = split_into_paragraphs(content)
        for i, paragraph in enumerate(paragraphs):
            documents.append({
                "source": file.name,
                "paragraph_id": f"{file.stem}_{i}",
                "text": paragraph
            })
    return documents

def generate_embeddings_ollama(docs: List[Dict], model_name: str) -> List[Dict]:
    """使用 Ollama 的 embedding API 產生向量，含 tqdm 進度條"""
    for doc in tqdm(docs, desc="🧠 Generating embeddings"):
        payload = {
            "model": model_name,
            "prompt": doc["text"]
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload)
            res.raise_for_status()
            result = res.json()
            doc["embedding"] = result["embedding"]
        except Exception as e:
            print(f"❌ 無法為段落產生 embedding: {doc['paragraph_id']} - {e}")
            doc["embedding"] = None
    return docs

def save_embeddings(docs: List[Dict], output_path: Path):
    """儲存結果為 JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

def main():
    if not DATA_DIR.exists():
        print(f"❌ 資料夾不存在：{DATA_DIR}")
        return

    print("🔍 載入資料中...")
    docs = load_documents(DATA_DIR)

    print(f"🧠 使用模型 {OLLAMA_MODEL} 產生 embedding 中...")
    docs = generate_embeddings_ollama(docs, OLLAMA_MODEL)

    print(f"💾 儲存至 {OUTPUT_PATH}")
    save_embeddings(docs, OUTPUT_PATH)
    print("✅ 完成！")

if __name__ == "__main__":
    main()
