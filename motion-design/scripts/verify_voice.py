"""Verify TTS clips: transcribe each one back with Gemini and flag every word that differs.

  python verify_voice.py [timeline.json] [line indexes...]

Numbers are normalised (84 == eighty-four, 96% == ninety-six percent, SDK == S D K) so only real
substitutions are flagged ("feature" heard as "future" fails). Regenerate a failing line with
  python voice.py script.json --only <i>
"""
import base64, json, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import voice

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def spell(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + spell(n % 100))
    return str(n)


def norm(s):
    s = s.lower().replace("%", " percent").replace("$", " dollars ").replace("-", " ")
    s = re.sub(r"\b([a-z])\s(?=[a-z]\b)", r"\1", s)                        # "s d k" -> "sdk"
    s = re.sub(r"\d+", lambda m: spell(m.group()), s)
    return re.sub(r"[^a-z ]", " ", s).split()


def main():
    args = sys.argv[1:]
    tl_path = args.pop(0) if args and args[0].endswith(".json") else "timeline.json"
    only = {int(a) for a in args}
    key = voice.find_key()
    if not key: sys.exit("no Gemini key (see VOICE.md)")
    tl = json.loads(Path(tl_path).read_text()); bad = []
    for l in tl["lines"]:
        if only and l["i"] not in only: continue
        b64 = base64.b64encode(Path(l["file"]).read_bytes()).decode()
        body = {"contents": [{"parts": [{"inline_data": {"mime_type": "audio/wav", "data": b64}},
                                        {"text": "Transcribe this audio word for word. Output only the words."}]}]}
        txt = ""
        for _ in range(3):
            j = voice._req(f"{voice.API}/models/gemini-flash-latest:generateContent", key, body)
            parts = j.get("candidates", [{}])[0].get("content", {}).get("parts")
            if parts: txt = parts[0]["text"].strip(); break
        a, h = norm(l["text"]), norm(txt)
        diff = []
        if "".join(a) != "".join(h):                                      # spacing-insensitive ("K P Is" == "KPIs")
            import difflib
            sm = difflib.SequenceMatcher(a=a, b=h)
            diff = [(" ".join(a[i1:i2]), " ".join(h[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"]
        print(f'{l["i"]:>2} {"OK  " if not diff else "FAIL"} | {txt}' + (f"   <- {diff[:4]}" if diff else ""))
        if diff: bad.append(l["i"])
    if bad: print("regenerate:", ",".join(map(str, bad)))


if __name__ == "__main__":
    main()
