"""Render a seek(t) film frame by frame with Playwright, encode with ffmpeg.

  python render.py probe 0.5 2 4.2 ...   -> probe/sheet.png (look at it)
  python render.py beats                 -> probe/beats.png, one frame per beat
  python render.py full [t0 t1]          -> out/video.mp4 (N subframes per frame blended with tmix = motion blur)
  python render.py pops [file]           -> single-frame pop scan

Serve the film folder first: python -m http.server <port> --directory <film> (background).
Env: W H (stage size, default 1920x1080), FPS (60), SUB (subframes, 8; use FPS=30 SUB=1 for drafts),
     T (duration; default window.TOTAL from the page), BPM (for `beats`, default 120),
     URL (default http://localhost:8000/film.html; ?w=&h= are appended so the page lays out for the format).
"""
import asyncio, os, shutil, subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from playwright.async_api import async_playwright

HERE = Path(__file__).parent
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = int(os.environ.get("W", 1920)), int(os.environ.get("H", 1080))
FPS, SUB = int(os.environ.get("FPS", 60)), int(os.environ.get("SUB", 8))
BPM = float(os.environ.get("BPM", 120))
BASE = os.environ.get("URL", "http://localhost:8000/film.html")
URL = BASE + ("&" if "?" in BASE else "?") + f"w={W}&h={H}"


async def open_page(p):
    b = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append("console: " + m.text) if m.type in ("error", "warning") else None)
    await pg.goto(URL)
    await pg.wait_for_function("window.ready === true", timeout=120000)
    total = float(os.environ.get("T") or await pg.evaluate("window.TOTAL || 0") or 10)
    return b, pg, errs, total


async def shot(pg, t, path, fmt="png"):
    await pg.evaluate(f"window.seek({t})")
    el = await pg.query_selector("#stage")
    await el.screenshot(path=str(path), type=fmt, **({"quality": 95} if fmt == "jpeg" else {}))


def sheet(folder, pattern, n, out, cols=4):
    rows = -(-n // cols)
    size = 360 if W >= H else 240
    subprocess.run([FF, "-v", "error", "-y", "-i", str(folder / pattern), "-vf",
                    f"scale={size}:-1,tile={cols}x{rows}:padding=6:color=white", "-frames:v", "1", str(out)], check=True)


async def probe(times=None, name="sheet.png", cols=4):
    out = HERE / "probe"; shutil.rmtree(out, ignore_errors=True); out.mkdir()
    async with async_playwright() as p:
        b, pg, errs, total = await open_page(p)
        if times is None:  # one frame per beat, slightly after the beat
            times = list(np.arange(60 / BPM * 0.9, total, 60 / BPM))
        for i, t in enumerate(times): await shot(pg, t, out / f"p_{i:03d}.png")
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    sheet(out, "p_%03d.png", len(times), out / name, cols=cols)
    print("probe:", len(times), "->", out / name)


async def full(t_from=None, t_to=None):
    sub = HERE / "sub"; shutil.rmtree(sub, ignore_errors=True); sub.mkdir()
    offs = [(j - (SUB - 1) / 2) / (FPS * SUB) for j in range(SUB)] if SUB > 1 else [0.0]
    async with async_playwright() as p:
        b, pg, errs, total = await open_page(p)
        a, z = (t_from or 0.0), (t_to or total)
        n, k = int(round((z - a) * FPS)), 0
        for i in range(n):
            for o in offs:
                t = min(total - 1e-3, max(0.0, a + i / FPS + o))
                await shot(pg, t, sub / f"s_{k:06d}.jpg", "jpeg"); k += 1
            if i % FPS == 0: print(f"frame {i}/{n}", flush=True)
        await b.close()
    if errs: print("PAGE ERRORS:", errs[:8])
    (HERE / "out").mkdir(exist_ok=True)
    vf = f"tmix=frames={SUB},select='eq(mod(n\\,{SUB})\\,{SUB - 1})',setpts=N/{FPS}/TB" if SUB > 1 else "null"
    vf += ",scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p"
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS * SUB), "-i", str(sub / "s_%06d.jpg"), "-vf", vf, "-r", str(FPS),
                    "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-color_range", "tv", "-colorspace", "bt709",
                    str(HERE / "out/video.mp4")], check=True)
    print("video ->", HERE / "out/video.mp4")


def pops(path=None):
    path = path or HERE / "out/video.mp4"
    raw = subprocess.run([FF, "-v", "quiet", "-i", str(path), "-vf", "scale=180:180,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 180, 180).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
    hits = []
    for i in range(1, len(d) - 1):
        nb = max(d[i - 1], d[i + 1], 0.3)
        if d[i] > 3 * nb and d[i] > 2.0: hits.append((i + 1, round((i + 1) / FPS, 3), round(float(d[i]), 2), round(float(nb), 2)))
    print("pops:", len(hits))
    for h in hits: print("  frame", h[0], "t", h[1], "diff", h[2], "neighbours", h[3])


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "probe": asyncio.run(probe([float(x) for x in sys.argv[2:]]))
    elif cmd == "beats": asyncio.run(probe(None, "beats.png", cols=8))
    elif cmd == "full": asyncio.run(full(*[float(x) for x in sys.argv[2:4]]))
    elif cmd == "pops": pops(sys.argv[2] if len(sys.argv) > 2 else None)
