"""Stock-track soundtrack: music offset so its drop lands on the film's key frame, SFX placed by measured peak,
tail fade, two-pass loudnorm to -14 LUFS.  Copy next to the film and edit the CONFIG block.

  python audio.py            -> out/audio.wav

events.json = [[t_seconds, "sfx/file.mp3", gain], ...]   (gain 0.04-0.3; one entry per visual event)
Find DROP_IN_SONG with analyze_song.py (band energy), never with an auto beat grid.
For a synthesised score instead, use synth.py.
"""
import json, subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg

# ---------------- CONFIG ----------------
HERE = Path(__file__).parent
TRACK = HERE / "assets/audio/track.mp3"   # free-licensed track (e.g. Mixkit)
DROP_IN_SONG = 16.0                       # seconds, measured
DROP_IN_FILM = 4.0                        # seconds: the key visual moment
T = 12.0                                  # film length
FADE_IN, FADE_OUT = 0.25, 0.9
EVENTS = HERE / "events.json"
# ----------------------------------------

FF, SR = imageio_ffmpeg.get_ffmpeg_exe(), 48000
N = int(round(T * SR)); START = DROP_IN_SONG - DROP_IN_FILM


def load(p):
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


song = load(TRACK)
s0 = int(max(0.0, START) * SR); pad = int(max(0.0, -START) * SR)   # negative START = silence before the song
mix = np.zeros((N, 2), np.float32)
seg = song[s0:s0 + N - pad]; mix[pad:pad + len(seg)] = seg
fi = int(FADE_IN * SR); mix[pad:pad + fi] *= np.linspace(0, 1, fi)[:, None]

cache = {}
for t, f, gain in (json.loads(EVENTS.read_text()) if EVENTS.exists() else []):
    if f not in cache: cache[f] = load(HERE / f)
    s = cache[f] / (np.abs(cache[f]).max() + 1e-9) * gain
    i0 = int(round(t * SR)) - int(np.abs(s).sum(1).argmax())       # the sample's peak lands on t
    lo, hi = max(0, i0), min(N, i0 + len(s))
    if hi > lo: mix[lo:hi] += s[lo - i0:hi - i0]

f0 = int((T - FADE_OUT) * SR); mix[f0:] *= np.linspace(1, 0, N - f0)[:, None] ** 1.3
rawp = HERE / "out/raw.wav"; rawp.parent.mkdir(exist_ok=True)
subprocess.run([FF, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(rawp)], input=mix.astype(np.float32).tobytes(), check=True)
m = subprocess.run([FF, "-hide_banner", "-i", str(rawp), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex("{"):m.rindex("}") + 1])
af = (f"loudnorm=I=-14:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
      f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,alimiter=limit=0.891:level=false")  # loudnorm can overshoot: cap at -1 dBTP
subprocess.run([FF, "-v", "error", "-y", "-i", str(rawp), "-af", af, "-ar", str(SR), str(HERE / "out/audio.wav")], check=True)
print("audio ->", HERE / "out/audio.wav")
