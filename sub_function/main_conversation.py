import sys
import time
import json
import platform
import signal
import subprocess
import requests

from conversation_handler import ConversationHandler

OLLAMA_URL = "http://localhost:11434/api/chat"

class ConversationController:
    def __init__(self, model="qwen2.5:3b", cot_enable=False, cot_prompt=None):
        self.model = model
        self.conversation_handler = ConversationHandler()
        self.conversation_id = self.conversation_handler.new_conversation(model)
        self.cot_enable = cot_enable
        self.cot_prompt = cot_prompt
        
        # If CoT is enabled, add the system prompt at the beginning
        if self.cot_enable and self.cot_prompt:
            self.conversation_handler.add_message("system", self.cot_prompt)
            
        print(f"🆕 Started new conversation with ID: {self.conversation_id}")

    def handle_command(self, command_line):
        cmd_parts = command_line.strip().split(maxsplit=1)
        command = cmd_parts[0].lower()

        if command == "/new":
            self._start_new_conversation()
            return True

        elif command == "/load" and len(cmd_parts) > 1:
            return self._load_conversation(cmd_parts[1])

        elif command == "/save":
            return self._save_conversation()

        elif command in ["/exit", "/quit", "/bye"]:
            self._exit_conversation()
            return True

        elif command == "/restart-ollama":
            self._restart_ollama()
            return True

        elif command == "/model" and len(cmd_parts) > 1:
            self._change_model(cmd_parts[1])
            return True

        return False

    # === 子功能 ===

    def _start_new_conversation(self):
        self.conversation_handler.save_conversation()
        self.conversation_id = self.conversation_handler.new_conversation(self.model)
        print(f"🆕 Started new conversation with ID: {self.conversation_id}")

    def _load_conversation(self, conv_id):
        if self.conversation_handler.load_conversation(conv_id):
            print(f"📂 Loaded conversation {conv_id}")
            history = self.conversation_handler.get_conversation_history()
            if history:
                print("🧠 Last messages:")
                for msg in history[-2:]:
                    print(f"\n{msg['role'].title()}: {msg['content']}")
            return True
        else:
            print(f"❌ Failed to load conversation {conv_id}")
            return True

    def _save_conversation(self):
        if self.conversation_handler.save_conversation():
            print(f"💾 Saved conversation {self.conversation_handler.current_id}")
        else:
            print("❌ No conversation to save")
        return True

    def _exit_conversation(self):
        self.conversation_handler.save_conversation()
        print("👋 Goodbye!")
        sys.exit(0)

    def _restart_ollama(self):
        print("♻️ Restarting Ollama server...")
        if platform.system() == "Windows":
            subprocess.call(["taskkill", "/F", "/IM", "ollama.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.call(["pkill", "-f", "ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
        subprocess.Popen(["ollama", "serve"])
        print("✅ Ollama server restarted.")

    def _change_model(self, new_model):
        self.model = new_model
        print(f"🤖 Model changed to: {self.model}")

    def chat_with_llm(self, user_input):
        self.conversation_handler.add_message("user", user_input)

        # 準備 messages 結構
        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_handler.get_conversation_history()
        ]

        try:
            response = requests.post(
                OLLAMA_URL,
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


    def chat_with_llm_stream(self, user_input, on_token=None, on_done=None):
        self.conversation_handler.add_message("user", user_input)

        messages = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_handler.get_conversation_history()
        ]

        try:
            response = requests.post(
                OLLAMA_URL,
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": self.model,
                    "messages": messages,
                    "stream": True
                }),
                stream=True
            )

            if response.status_code != 200:
                if on_done:
                    on_done(f"\n❌ Failed: {response.status_code}")
                return

            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if "message" in chunk and "content" in chunk["message"]:
                            content = chunk["message"]["content"]
                            if content:
                                full_response += content
                                if on_token:
                                    on_token(content)
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue

            self.conversation_handler.add_message("assistant", full_response)
            if on_done:
                on_done(None)

        except Exception as e:
            if on_done:
                on_done(f"\n❌ Error: {e}")

# =============================
# ✅ 可以直接執行測試指令 + Ollama 回應
# =============================
if __name__ == "__main__":
    # CoT configuration
    CoT_enable = True  # don't use this in reasoning models
    CoT_Prompt = """
    You are a reasoning assistant.
    You must always put all reasoning steps inside a <think>...</think> block.
    Do not output any reasoning outside of <think>.
    After <think>, clearly write the final answer.

    Format:
    <think>
    Step 1: ...
    Step 2: ...
    </think>
    The answer is: ...
    """
    
    # Initialize with CoT parameters when enabled
    if CoT_enable:
        ctrl = ConversationController(model="qwen2.5:3b", cot_enable=CoT_enable, cot_prompt=CoT_Prompt)
    else:
        ctrl = ConversationController(model="qwen3:4b")
    
    print("\n✅ 支援指令: /new, /load <id>, /save, /model <n>, /restart-ollama, /exit")

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if ctrl.handle_command(user_input):
                continue

            ctrl.chat_with_llm(user_input)

        except KeyboardInterrupt:
            print("\n🛑 KeyboardInterrupt detected")
            ctrl._exit_conversation()
