"""Brings every voice clip to the same speech loudness (RMS of voiced samples) with a 0.95 peak ceiling."""
import soundfile as sf, numpy as np
TARGET = 0.17
for k in ['narrator', 'sheldon1', 'leonard1', 'sheldon2', 'penny1', 'sheldon3']:
    p = f'public/audio/{k}.wav'; a, sr = sf.read(p)
    v = a[np.abs(a) > 0.02]; g = min(TARGET / np.sqrt((v ** 2).mean()), 0.95 / np.abs(a).max())
    sf.write(p, (a * g).astype(np.float32), sr); print(k, round(g, 2))
