import os
import json
import requests
import base64

class ImageAnalyzer:
    def __init__(self, vision_model="llama3.2-vision"):
        self.vision_model = vision_model
        self.ollama_url = "http://localhost:11434/api/chat"

    def encode_image_to_base64(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Error reading image: {e}")
            return None

    def analyze_image(self, image_path, prompt="Please describe this image in detail."):
        absolute_path = os.path.abspath(image_path)

        if not os.path.exists(absolute_path):
            print(f"❌ File not found: {absolute_path}")
            return

        image_data = self.encode_image_to_base64(absolute_path)
        if not image_data:
            print("❌ Failed to encode image.")
            return

        messages = [
            {
                "role": "user",
                "content": prompt,
                "images": [image_data]
            }
        ]

        try:
            response = requests.post(
                self.ollama_url,
                headers={"Content-Type": "application/json"},
                data=json.dumps({
                    "model": self.vision_model,
                    "messages": messages,
                    "stream": True
                }),
                stream=True
            )

            if response.status_code != 200:
                print(f"❌ Vision model error: {response.status_code}")
                print(response.text)
                return

            print(f"\n🖼️ Analyzing: {os.path.basename(image_path)}")
            print("Assistant: ", end="", flush=True)
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
            return full_response

        except Exception as e:
            print(f"❌ Error analyzing image: {e}")


# ============================
# ✅ 測試模式
# ============================
if __name__ == "__main__":
    print("🧪 Image Analysis CLI Mode")
    path = input("📂 請輸入圖片路徑：").strip()
    analyzer = ImageAnalyzer()
    analyzer.analyze_image(path)
