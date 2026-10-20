"""Generate each line with its own Kokoro voice; trim silence; print durations (s)."""
import sys, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
model, voices, out = sys.argv[1:4]
k = Kokoro(model, voices)
LINES = [("narrator", "bm_george", 1.08, "For Sheldon Cooper, even a couch has rules."),
         ("sheldon1", "am_eric", 1.1, "Why have you moved it?"),
         ("leonard1", "am_michael", 1.08, "I needed space for the food."),
         ("sheldon2", "am_eric", 1.12, "The seating arrangement follows a specific geometry."),
         ("penny1", "af_heart", 1.0, "Looks comfy."),
         ("sheldon3", "am_eric", 1.08, "This is precisely why we need rules.")]
res = {}
for key, voice, speed, text in LINES:
    a, sr = k.create(text, voice=voice, speed=speed, lang="en-gb" if voice.startswith("b") else "en-us")
    e = np.abs(a) > 0.01; i = max(0, np.argmax(e) - int(.03 * sr)); j = min(len(a), len(a) - np.argmax(e[::-1]) + int(.10 * sr))
    a = a[i:j]; sf.write(f"{out}/{key}.wav", a, sr); res[key] = round(len(a) / sr, 3)
print(json.dumps(res))
