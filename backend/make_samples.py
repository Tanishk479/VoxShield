import math
import os
import struct
import wave

os.makedirs("test_samples", exist_ok=True)

samples = ["safe", "hospital_emergency", "digital_arrest"]
sample_rate = 16000
duration_sec = 3
num_samples = sample_rate * duration_sec

for name in samples:
    file_path = os.path.join("test_samples", f"{name}.wav")
    with wave.open(file_path, "wb") as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Distinct frequency tone for each scenario
        freq = 300 if name == "safe" else (600 if name == "hospital_emergency" else 900)
        raw_data = bytearray()

        for i in range(num_samples):
            value = int(8000 * math.sin(2 * math.pi * freq * (i / sample_rate)))
            raw_data.extend(struct.pack("<h", value))

        wav_file.writeframes(raw_data)

    print(f"Generated: {file_path}")

print("All audio samples generated successfully.")