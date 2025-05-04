import re
import requests
import subprocess
import platform
import time
import json

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"

ENHANCED_PROMPT_TEMPLATE = """
You are a task dispatcher. Your job is to classify the user's request and select exactly ONE model to handle it.

Available models:
- reasoning: Used when the user wants logical thinking, problem solving, math, analysis, or deep reasoning.
- intuition: Used when the user wants an opinion, feeling, judgment, or abstract idea.
- img-gen: When the user wants to generate images.
- img2txt: When the user uploads an image and wants a description of its contents.
- tts: When the user wants text read out loud.
- stt: When the user provides audio and wants a transcription.
- music-gen: When the user wants music generated.

Always return ONLY one of the following in the format: <model>...</model>
DO NOT explain. DO NOT include anything else. Strictly output one of the options.

User: 我想要解一個數學問題，關係到相機參數
Response: <model>reasoning</model>

User: 我希望你進行深度思考
Response: <model>reasoning</model>

User: {{ user_input }}
"""

QUICK_COMMANDS = [
    "/reasoning",
    "/intuition",
    "/img-gen",
    "/img2txt",
    "/tts",
    "/stt",
    "/music-gen",
]

class DispatcherController:
    def __init__(self):
        self.model = OLLAMA_MODEL
        self.history = []
        self._ensure_ollama_running()

    def _ensure_ollama_running(self):
        try:
            requests.get(OLLAMA_URL, timeout=1)
        except:
            print("🟡 Ollama 未啟動，正在啟動中...")
            if platform.system() == "Windows":
                subprocess.Popen(["ollama", "serve"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            print("✅ Ollama server 啟動完成")

    def dispatch(self, user_input: str) -> str:
        self.history.append({"role": "user", "content": user_input})

        # ✅ 快速指令跳過模型判斷
        shortcut_match = re.match(r"/(reasoning|intuition|img-gen|img2txt|tts|stt|music-gen)", user_input.strip().lower())
        if shortcut_match:
            model_type = shortcut_match.group(1)
            model_tag = f"<model>{model_type}</model>"
            print(f"⚡ 快速指令觸發：{model_tag}")
            return model_tag

        prompt = ENHANCED_PROMPT_TEMPLATE.replace("{{ user_input }}", user_input)

        messages = [
            {"role": "system", "content": "You are a helpful task routing assistant."},
            {"role": "user", "content": prompt}
        ]

        try:
            response = requests.post(
                OLLAMA_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0
                    }
                })
            )

            if response.status_code != 200:
                print(f"❌ Failed to get model prediction: {response.status_code}")
                return "<model>intuition</model>"

            data = response.json()
            full_output = data.get("message", {}).get("content", "").strip()

            print("📝 模型回應：")
            print(full_output)

            self.history.append({"role": "assistant", "content": full_output})

            # 提取 <model>xxx</model>
            match = re.search(r"<model>(.*?)</model>", full_output, re.IGNORECASE)
            if match:
                model_tag = f"<model>{match.group(1).strip()}</model>"
                return model_tag
            else:
                print("⚠️ 無法從回應中提取模型，自動回退為 intuition")
                return "<model>intuition</model>"

        except Exception as e:
            print(f"❌ Error communicating with Ollama: {e}")
            return "<model>intuition</model>"


# =============================
# ✅ 測試：互動式輸入
# =============================
if __name__ == "__main__":
    dispatcher = DispatcherController()

    print("\n🤖 Dispatcher ready. 請輸入任務描述（Ctrl+C 離開）：")
    print("💡 快速指令：可跳過模型推論直接輸出")
    for cmd in QUICK_COMMANDS:
        print(f"   {cmd}")

    while True:
        try:
            user_input = input("\n👤 User: ").strip()
            if not user_input:
                continue
            output = dispatcher.dispatch(user_input)
            print(f"🎯 模型判斷結果: {output}")
        except KeyboardInterrupt:
            print("\n🛑 Dispatcher 結束")
            break
