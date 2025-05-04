from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QTextCursor
import sys
import time

from main_conversation import ConversationController  # 請確保此檔案存在且包含 ConversationController


# === LLM Streaming Thread ===
class ChatThread(QThread):
    token_received = Signal(str)
    finished_stream = Signal()

    def __init__(self, controller, user_input):
        super().__init__()
        self.controller = controller
        self.user_input = user_input

    def run(self):
        def on_token(token):
            self.token_received.emit(token)

        def on_done(error_msg):
            if error_msg:
                self.token_received.emit(error_msg)
            self.finished_stream.emit()

        self.controller.chat_with_llm_stream(
            self.user_input,
            on_token=on_token,
            on_done=on_done
        )


# === Background Sync Thread for terminal assistant output ===
class SyncThread(QThread):
    sync_update = Signal(str)

    def __init__(self, controller, get_last_assistant_index):
        super().__init__()
        self.controller = controller
        self.get_last_assistant_index = get_last_assistant_index
        self.running = True
        self.last_len = 0

    def run(self):
        while self.running:
            time.sleep(0.5)
            history = self.controller.conversation_handler.get_conversation_history()
            gui_last_idx = self.get_last_assistant_index()

            if len(history) > self.last_len:
                for i, msg in enumerate(history[self.last_len:], start=self.last_len):
                    if msg["role"] == "assistant" and i >= gui_last_idx:
                        self.sync_update.emit(f"🤖 Assistant: {msg['content']}")
                self.last_len = len(history)

    def stop(self):
        self.running = False


# === GUI Window ===
class ChatWindow(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.setWindowTitle("🧠 Ollama Terminal Chat GUI")
        self.resize(640, 500)

        self.layout = QVBoxLayout(self)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        self.text_input = QLineEdit(self)
        self.text_input.returnPressed.connect(self.send_message)

        self.layout.addWidget(self.text_display)
        self.layout.addWidget(self.text_input)

        self.controller = controller
        self.append_text("🟢 Connected to model: " + self.controller.model)

        self.current_output = ""
        self.last_assistant_index = 0

        self.sync_thread = SyncThread(self.controller, lambda: self.last_assistant_index)
        self.sync_thread.sync_update.connect(self.append_text)
        self.sync_thread.start()

    def append_text(self, text):
        self.text_display.append(text)

    def append_text_token(self, token):
        self.current_output += token
        self.text_display.moveCursor(QTextCursor.End)
        self.text_display.insertPlainText(token)
        self.text_display.moveCursor(QTextCursor.End)

    def chat_done(self):
        self.append_text("")  # 換行
        self.last_assistant_index = len(self.controller.conversation_handler.get_conversation_history())

    def send_message(self):
        user_input = self.text_input.text().strip()
        if not user_input:
            return

        self.append_text(f"🧑 You: {user_input}")
        self.append_text("🤖 Assistant: ")  # 為接下來 token 留出一行
        self.text_input.clear()

        if self.controller.handle_command(user_input):
            self.append_text("⚙️ Command handled.")
            return

        self.current_output = ""
        self.chat_thread = ChatThread(self.controller, user_input)
        self.chat_thread.token_received.connect(self.append_text_token)
        self.chat_thread.finished_stream.connect(self.chat_done)
        self.chat_thread.start()

    def closeEvent(self, event):
        self.sync_thread.stop()
        super().closeEvent(event)


# === 主程式 ===
if __name__ == "__main__":
    controller = ConversationController(model="qwen2.5:3b")
    print("✅ GUI mode active. You can still use terminal as well.")

    app = QApplication(sys.argv)
    win = ChatWindow(controller)
    win.show()
    sys.exit(app.exec())
