import whisper
import sounddevice as sd
import numpy as np
import tempfile
import scipy.io.wavfile
import time

# === 參數設定 ===
DURATION = 5  # 每次錄音秒數
SAMPLE_RATE = 16000  # Whisper 建議用 16kHz
MODEL_NAME = "small"  # 模型大小，可改為 medium/large 等

# === 載入模型（一次即可）===
print("🔄 Loading Whisper model...")
model = whisper.load_model(MODEL_NAME)
print("✅ Model loaded.")

print(f"🎙️ 開始循環錄音，每次 {DURATION} 秒，Ctrl+C 可停止")

try:
    while True:
        print(f"\n🎤 錄音中 ({DURATION} 秒)... 請開始說話")
        recording = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            scipy.io.wavfile.write(tmpfile.name, SAMPLE_RATE, (recording * 32767).astype(np.int16))
            print("🧠 正在轉換語音為文字...")
            result = model.transcribe(tmpfile.name)

        print("📝 辨識結果：")
        print(result["text"])
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\n🛑 已中止語音辨識。")
