from transformers import MusicgenForConditionalGeneration, AutoProcessor
import torchaudio
import os

model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")

inputs = processor(text=["a relaxing lo-fi beat with rain sounds"], return_tensors="pt")
audio_values = model.generate(**inputs, max_new_tokens=800)

output_dir = "MusicGen_output"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "output.wav")
torchaudio.save(output_path, audio_values[0], 32000)
