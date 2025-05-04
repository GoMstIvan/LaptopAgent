from TTS.api import TTS  # 需要安裝Visual Studio C++的MSVC、Windows SDK、CMake等工具
import sounddevice as sd
import torch
from TTS.utils.radam import RAdam  # 👈 需要明確 import
from collections import defaultdict

safe_classes = [RAdam, defaultdict, dict, list, tuple, set, slice, complex]

with torch.serialization.safe_globals({cls: None for cls in safe_classes}):
    from TTS.api import TTS
    tts_chinese = TTS(model_name="tts_models/zh-CN/baker/tacotron2-DDC-GST", progress_bar=False)
    tts_english = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)

while True:
    text = input("請輸入要轉換的中文字（或輸入 'exit' 退出）：")
    text += "。"  # 少了的話會無限循環
    # 🎧 使用 TTS 模型產生語音波形
    audio = tts_chinese.tts(text)

    # 🔊 播放（不存檔）
    sd.play(audio, samplerate=tts_chinese.synthesizer.output_sample_rate)
    sd.wait()

    text = input("請輸入要轉換的英文句子（或輸入 'exit' 退出）：")
    text += "."  # 少了的話會無限循環
    audio = tts_english.tts(text)
    sd.play(audio, samplerate=tts_english.synthesizer.output_sample_rate)
    sd.wait()