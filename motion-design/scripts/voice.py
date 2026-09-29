"""Voice-over: script.json -> one WAV per line -> trimmed -> timeline.json (the picture reads it).

  python voice.py script.json [--engine gemini|say|auto] [--voice NAME] [--out voice/]

script.json = [["chapter", "line text"], ...]  (write for the ear; numbers spelled as spoken)
Engines:
  gemini : Gemini TTS. Key from $GEMINI_API_KEY, ~/.config/gemini/key, or ./.env (GEMINI_API_KEY=...). Never printed.
  say    : macOS `say` (keyless, lower quality). Picks an Enhanced/Premium voice if installed, else Samantha.
  auto   : gemini if a key is found, else say (with a warning). Default is gemini: no key = stop, so the
           low-quality fallback is never chosen silently; use `say` only once the user has picked it.
Output: voice/line_XX.wav (44.1 kHz mono), timeline.json = {lines:[{i,ch,text,start,dur,file}], total, engine, voice}
Timing: first line at 1.2 s, 0.45 s between lines, +0.9 s at a chapter change, 2.5 s tail.
"""
import argparse, base64, concurrent.futures as cf, json, os, re, subprocess, sys, time, urllib.request, wave
from pathlib import Path

try:
    import imageio_ffmpeg
    FF = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FF = "ffmpeg"
API = "https://generativelanguage.googleapis.com/v1beta"


def find_key():
    if os.environ.get("GEMINI_API_KEY"): return os.environ["GEMINI_API_KEY"].strip()
    p = Path.home() / ".config/gemini/key"
    if p.exists() and p.stat().st_size: return p.read_text().strip()
    for env in (Path(".env"), Path("../.env")):
        if env.exists():
            for ln in env.read_text().splitlines():
                if ln.startswith("GEMINI_API_KEY="): return ln.split("=", 1)[1].split("#")[0].strip().strip('"\'')  # drop inline comments
    return None


def _req(url, key, body=None):
    r = urllib.request.Request(url, data=json.dumps(body).encode() if body else None,
                               headers={"x-goog-api-key": key, "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=120) as f: return json.loads(f.read())


def gemini_model(key):
    names = [m["name"] for m in _req(f"{API}/models?pageSize=200", key).get("models", []) if "tts" in m["name"]]
    flash = sorted([n for n in names if "flash" in n]) or sorted(names)
    if not flash: sys.exit("no TTS model visible for this key")
    return flash[-1]


def gemini_line(key, model, text, voice, path):
    body = {"contents": [{"parts": [{"text": text}]}],  # plain line only: a style prefix gets read aloud
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    for attempt in range(4):
        try:
            j = _req(f"{API}/{model}:generateContent", key, body)
            part = j["candidates"][0]["content"]["parts"][0]["inlineData"]
            raw = base64.b64decode(part["data"])
            tmp = path.with_suffix(".src.wav")
            if raw[:4] == b"RIFF": tmp.write_bytes(raw)            # newer models: full WAV
            else:                                                  # older: raw L16 PCM 24 kHz
                with wave.open(str(tmp), "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(raw)
            return tmp
        except Exception as e:
            if attempt == 3: raise
            time.sleep(2 * (attempt + 1))


def say_voice(pref):
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout.splitlines()
    names = [re.split(r"\s{2,}", l.strip())[0] for l in out if "en_" in l]
    if pref and any(n.startswith(pref) for n in names): return next(n for n in names if n.startswith(pref))
    for tag in ("(Premium)", "(Enhanced)"):
        c = [n for n in names if tag in n]
        if c: return c[0]
    return "Samantha" if "Samantha" in names else (names[0] if names else None)


def say_line(text, voice, path):
    tmp = path.with_suffix(".src.aiff")
    subprocess.run(["say", "-v", voice, "-o", str(tmp), text], check=True)
    return tmp


def trim(src, dst):
    s = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05"
    subprocess.run([FF, "-v", "error", "-y", "-i", str(src), "-af", f"{s},areverse,{s},areverse", "-ac", "1", "-ar", "44100", str(dst)], check=True)
    with wave.open(str(dst)) as w: return w.getnframes() / w.getframerate()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script"); ap.add_argument("--engine", default="gemini"); ap.add_argument("--voice", default=None)
    ap.add_argument("--out", default="voice")
    ap.add_argument("--only", default="", help="comma-separated line indexes to regenerate; other clips are kept")
    a = ap.parse_args()
    lines = json.loads(Path(a.script).read_text())
    out = Path(a.out); out.mkdir(exist_ok=True)
    key = find_key() if a.engine in ("auto", "gemini") else None
    engine = "gemini" if key else "say"
    if a.engine == "gemini" and not key: sys.exit("no Gemini key found: ask the user where it is or whether to use the macOS voice (VOICE.md), never in chat")
    if a.engine == "auto" and not key: print("WARNING: no Gemini key, falling back to macOS `say` (lower quality). Tell the user.", file=sys.stderr)
    todo = [int(x) for x in a.only.split(",") if x.strip()] or list(range(len(lines)))
    srcs = [out / f"line_{k:02d}.wav" for k in range(len(lines))]   # kept clips are re-trimmed (idempotent)
    if engine == "gemini":
        model, voice = gemini_model(key), a.voice or "Kore"
        with cf.ThreadPoolExecutor(4) as ex:
            for k, src in zip(todo, ex.map(lambda k: gemini_line(key, model, lines[k][1], voice, out / f"line_{k:02d}.wav"), todo)): srcs[k] = src
    else:
        voice = say_voice(a.voice)
        for k in todo: srcs[k] = say_line(lines[k][1], voice, out / f"line_{k:02d}.wav")
    tl, t, prev = [], 1.2, None
    for k, ((ch, text), src) in enumerate(zip(lines, srcs)):
        if prev is not None and ch != prev: t += 0.9
        dst = out / f"line_{k:02d}.wav"
        if src == dst: src = src.rename(dst.with_suffix(".keep.wav"))
        dur = trim(src, dst); src.unlink(missing_ok=True)
        tl.append({"i": k, "ch": ch, "text": text, "start": round(t, 3), "dur": round(dur, 3), "file": f"{out.name}/line_{k:02d}.wav"})
        t += dur + 0.45; prev = ch
    total = round(t - 0.45 + 2.5, 3)
    Path("timeline.json").write_text(json.dumps({"lines": tl, "total": total, "engine": engine, "voice": voice}, indent=1))
    print(f"engine={engine} voice={voice} lines={len(tl)} total={total}s -> timeline.json")


if __name__ == "__main__":
    main()
