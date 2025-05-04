import os
import time
import requests
import base64
import subprocess
from datetime import datetime

# === ✅ 設定項 ===
CONDA_ENV = "ultralytics"  # 你的 Conda 環境名稱
WEBUI_DIR = r"C:\Users\User\Desktop\OllamaAgent\stable-diffusion-webui"  # WebUI 資料夾
API_URL = "http://127.0.0.1:7860"
TXT2IMG_URL = f"{API_URL}/sdapi/v1/txt2img"
OPTIONS_URL = f"{API_URL}/sdapi/v1/options"
MODELS_URL = f"{API_URL}/sdapi/v1/sd-models"
OUTPUT_DIR = "stable_diffusion_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === ✅ WebUI 啟動檢查 ===
def is_webui_running() -> bool:
    try:
        res = requests.get(MODELS_URL, timeout=3)
        return res.status_code == 200
    except:
        return False

def launch_webui():
    print("🚀 Stable Diffusion WebUI not running, launching it...")
    command = f'conda run -n {CONDA_ENV} python launch.py --api'
    subprocess.Popen(command, cwd=WEBUI_DIR, shell=True)
    print("🕐 Waiting for WebUI to start...")

    for i in range(60):
        if is_webui_running():
            print("✅ WebUI is now running.")
            return True
        time.sleep(2)
    print("❌ Timeout: WebUI did not start within 60 seconds.")
    return False

# === ✅ 模型相關操作 ===
def list_available_models():
    try:
        res = requests.get(MODELS_URL)
        res.raise_for_status()
        models = res.json()
        print("📦 Available Models:")
        for m in models:
            print(f" - {m['title']} ({m['model_name']})")
        return [m['title'] for m in models]
    except Exception as e:
        print(f"❌ Error listing models: {e}")
        return []

def switch_model(model_name: str):
    try:
        payload = {"sd_model_checkpoint": model_name}
        res = requests.post(OPTIONS_URL, json=payload)
        res.raise_for_status()
        print(f"✅ Model switched to: {model_name}")
    except Exception as e:
        print(f"❌ Failed to switch model: {e}")

# === ✅ 產圖 ===
def generate_image_from_prompt(prompt: str, width=640, height=832, steps=28, cfg_scale=8.5):
    payload = {
        "prompt": prompt,
        "negative_prompt": "low quality, worst quality, blurry, bad anatomy, watermark, extra limbs, text",
        "width": width,
        "height": height,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_index": "Euler a"
    }

    try:
        print(f"🎨 Generating image for prompt: {prompt}")
        res = requests.post(TXT2IMG_URL, json=payload)
        res.raise_for_status()
        image_data = res.json()["images"][0]
        img = base64.b64decode(image_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{OUTPUT_DIR}/txt2img_{timestamp}.png"
        with open(filename, "wb") as f:
            f.write(img)

        print(f"✅ Image saved: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return None

# === ✅ 主程式 ===
if __name__ == "__main__":
    if not is_webui_running():
        if not launch_webui():
            exit("❌ Failed to launch WebUI.")

    models = list_available_models()
    # 👉 請替換下方為你實際看到的模型名稱（含 hash）
    model_to_use = "v1-5-pruned-emaonly.safetensors [6ce0161689]"
    if model_to_use in models:
        switch_model(model_to_use)
    else:
        print(f"⚠️ 模型 {model_to_use} 不在可用列表中，請確認名稱是否正確。")

    # ✅ 實際產圖
    prompt = "masterpiece, best quality, 1girl, white dress, floating, sunlight, backlight, cinematic"
    generate_image_from_prompt(prompt)
