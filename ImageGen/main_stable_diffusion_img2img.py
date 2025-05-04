import os
import time
import base64
import requests
import subprocess
from datetime import datetime

# === 🔧 設定項 ===
CONDA_ENV = "ultralytics"  # 請填入你的 Conda 環境名稱
WEBUI_DIR = r"C:\Users\User\Desktop\OllamaAgent\stable-diffusion-webui"  # Stable Diffusion WebUI 根目錄
API_BASE_URL = "http://127.0.0.1:7860"
IMG2IMG_URL = f"{API_BASE_URL}/sdapi/v1/img2img"
CHECK_URL = f"{API_BASE_URL}/sdapi/v1/sd-models"

INPUT_DIR = "stable_diffusion_input"
OUTPUT_DIR = "stable_diffusion_output"
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# === ✅ 檢查 WebUI 是否已啟動 ===
def is_webui_running() -> bool:
    try:
        res = requests.get(CHECK_URL, timeout=3)
        return res.status_code == 200
    except:
        return False

# === ✅ 若沒啟動則執行 WebUI ===
def launch_webui():
    print("🚀 WebUI not running. Launching with Conda env...")
    command = f'conda run -n {CONDA_ENV} python launch.py --api'
    subprocess.Popen(command, cwd=WEBUI_DIR, shell=True)
    print("🕐 Waiting for WebUI to start...")

    for i in range(60):
        if is_webui_running():
            print("✅ WebUI is now running.")
            return True
        time.sleep(2)

    print("❌ WebUI failed to start after timeout.")
    return False

# === ✅ 找出第一張圖片 ===
def get_first_image_path():
    files = sorted([
        f for f in os.listdir(INPUT_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ])
    return os.path.join(INPUT_DIR, files[0]) if files else None

# === ✅ 發送 img2img API 請求 ===
def generate_img2img(prompt: str, denoising_strength=0.55, steps=25, cfg_scale=7.5):
    image_path = get_first_image_path()
    if not image_path:
        print("❌ No image found in stable_diffusion_input/")
        return None

    print(f"📥 Using input image: {image_path}")

    with open(image_path, "rb") as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "init_images": [image_base64],
        "prompt": prompt,
        "denoising_strength": denoising_strength,
        "steps": steps,
        "cfg_scale": cfg_scale,
        "sampler_index": "Euler a"
    }

    try:
        print(f"🎨 Generating image from prompt: {prompt}")
        res = requests.post(IMG2IMG_URL, json=payload)
        res.raise_for_status()
        result_image_data = res.json()["images"][0]
        result_bytes = base64.b64decode(result_image_data)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(OUTPUT_DIR, f"img2img_{timestamp}.png")

        with open(output_path, "wb") as f:
            f.write(result_bytes)

        print(f"✅ Image saved: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Error during img2img: {e}")
        return None

# === ✅ 主程式入口 ===
if __name__ == "__main__":
    if not is_webui_running():
        if not launch_webui():
            exit("❌ Failed to launch WebUI. Exiting.")

    prompt = "masterpiece, best quality, cinematic lighting, glowing effects, 1girl"
    generate_img2img(prompt)
