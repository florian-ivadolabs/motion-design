---
name: motion-design
description: Direct and build a finished motion-design video 100 % in code (HTML seek(t) engine rendered frame by frame with Playwright + ffmpeg; no After Effects, no Remotion licence). Use when the user wants a video made: launch film, promo, product demo, explainer, personal/brand teaser, logo sting, showreel, LinkedIn/X/Reels clip, a narrated video, "remake this video for my brand", or to change a video's music, SFX or voice. Covers research → concept → beat map → stills → engine → render → music/SFX/voice → critique loop → delivery. Not for writing prompts for a text-to-video model.
---

# Motion design, 100 % code

You are the **director** and the whole crew. The film is one HTML page whose every frame is a pure function of time (`window.seek(t)`), rendered frame by frame by Playwright and encoded by ffmpeg. Music, SFX and voice are placed on the same clock. Everything is code, so any note becomes a small edit and a re-render. Deterministic, free (Chromium, ffmpeg, Python), licence-clean.

Reference files, read when you reach that step:
- [DIRECTION.md](DIRECTION.md): research, style reference, concept (mine the material, diverge, swap test, three storyboards), beat sheet, taste rules, turning notes into camera notes, delivery. **Read before any concept work.**
- [DEMO.md](DEMO.md): films over real product screens: capture, flipbooks of async states, camera and overlays, optional tutorial patterns.
- [ENGINE.md](ENGINE.md): the `seek(t)` engine and its idioms (springs, camera, masked type, floods, portal dives, formats).
- [AUDIO.md](AUDIO.md): stock music with the drop on the key frame, SFX by measured peak, loudness, or a fully synthesised score (`scripts/synth.py`).
- [VOICE.md](VOICE.md): narrated films (Gemini TTS, keyless macOS fallback, `timeline.json` drives the picture, ducking). `scripts/voice.py`.
- [ASSETS.md](ASSETS.md): free sources for photos, video, logos, icons, fonts, components, and how to vet them.
- [REMAKE.md](REMAKE.md): frame-locked 1:1 remake of a reference video (`scripts/remake/`).

Setup (once per machine): `uv venv ~/.venvs/motion-design && uv pip install --python ~/.venvs/motion-design/bin/python playwright imageio-ffmpeg numpy pillow && ~/.venvs/motion-design/bin/python -m playwright install chromium`. Work in the project folder the user names, else the session scratchpad; one folder per film: `film.html` + `render.py` (copy of `scripts/render_template.py`) + `audio.py` + `out/`.

## 0. Non-negotiables
- **Zero fabrication on screen.** Every figure comes from a source you read; drop ambiguous or conflicting numbers. Anything illustrative is labelled on screen ("Example data", "Illustration"). Never claim product features that don't exist. Keep a fact-check list for delivery.
- **Captions stay true**: no "made in 10 minutes", "one shot" or "no tools" unless literally true.
- **Clients, faces, logos of third parties** only from the user's own material; remind them to check clearance. No co-marks that imply a partnership.
- **Copyrighted music**: never reuse it. If the user names a track, use a free track in that style or synthesise an original (AUDIO.md) and say so.
- **Real product screens** are captured (Playwright screenshots), never invented; if blocked, ask for screenshots or label a recreation as illustrative.
- Respect the user's copy preferences (language, punctuation, tone) if they state them; remember them for the session.

## 1. The direction loop (always in this order)
1. **Inputs & research** (DIRECTION.md §1). If the brief has an `<inputs>` block, ask for it (AskUserQuestion, recommended defaults first); otherwise pick sensible defaults and say so. Research the subject yourself (site, docs, decks, public profile; LinkedIn is login-walled, work around it or ask for screenshots). Collect real numbers with sources, brand colours, logo, fonts, real screens.
2. **Style reference** (DIRECTION.md §2): the one the user names, else 1–2 pieces from a curated source (e.g. whatships.com). Sample frames every 0.5–3 s and write `docs/style_guide.md` (palette, type, shot length, transitions, camera). Take the grammar, never the content.
3. **Concept, then three storyboards** (DIRECTION.md §3): mine the material, diverge, then three genuinely different films, not three colourways. Show a short table with your pick and why each loser lost; continue on your pick unless the user asked to choose.
4. **Beat map** (`BEATMAP.md`): BPM → frames per beat, every scene and reveal on the grid, the music **drop on the key visual moment**. Nothing still for more than ~1 s, text holds ≥ 2.5 s and ~1 s per 3 words.
5. **Stills before motion**: render 4+ stills or one frame per beat (`render.py probe|beats`), **look at them**, fix framing, legibility, overlap; send the sheet to the user and keep working.
6. **Audio**: music + SFX by peak, or synthesised score; voice first if narrated (the voice drives the timeline). If narrated, check for a Gemini key at the start (VOICE.md); if none, ask where it is or whether the lower-quality macOS voice is fine: never fall back silently.
7. **Full render** → pop scan → mux → **critique loop** (§4) until every score is 8+.
8. **Deliver** (DIRECTION.md §6): the MP4 in the working directory, a scene table, the fact-check list, the cheap knobs (length, a line of copy, voice, music, format).

## 2. Render (scripts/render_template.py)
- Serve the film folder: `python -m http.server <free port> --directory <film>` (background). Pick a port nobody else uses.
- `render.py` reads `W H FPS T SUB URL` from env (defaults 1920×1080, 60 fps, 8 subframes). Formats: 1920×1080 (16:9), 1080×1920 (9:16 Reels/Stories/LinkedIn mobile), 1080×1350 (4:5 LinkedIn feed), 1080×1080 (1:1).
- `probe t1 t2…` → `probe/sheet.png`; `beats` → one frame per beat; `full` → N subframes per frame blended with `tmix` (motion blur; 6–8 for fast moves, 4 ghosts); `pops` → single-frame spikes > 3× neighbours (intentional cuts appear too: say so).
- Cost: ~1–1.5 min wall time per film second at 60 fps × 8 subframes. For drafts use `FPS=30 SUB=1`. Run long renders in the background; one folder per version so parallel renders don't clash.
- Final encode: `scale=in_range=pc:out_range=tv:out_color_matrix=bt709,format=yuv420p`, `-color_range tv -colorspace bt709`, libx264 crf 16, AAC 256k, `+faststart`.

## 3. Gotchas (all hit for real)
- Hash-only `goto` doesn't reload: set state via `page.evaluate`. `window.ready = true` only after `document.fonts.ready` and every image/video decoded.
- Measure text with canvas `measureText` (set `ctx.letterSpacing`), not DOM rects, when a camera scale is applied.
- Sharp text during a handoff: never scale a blurry copy, crossfade only the fill.
- Some APIs behind Cloudflare reject Python's default UA: send a normal `User-Agent`.
- Sandboxed shells may forbid heredocs, `cd && …` chains or `$(…)`: write small `.py` scripts and run plain commands. Quote paths with spaces or use a symlink.
- Long renders: start them in the background, write their PID to `out/render.pid`, and stop only that PID. Never `pkill -f` a pattern: other renders on the machine match it. Resume a killed render with `render.py full t0 t1` from where it stopped, then concatenate.
- If ffmpeg isn't on PATH: `imageio_ffmpeg.get_ffmpeg_exe()`.
- Platform specs: LinkedIn 4:5 or 9:16 (keep key content out of the bottom ~15 % and top ~8 % on 9:16, where UI overlays sit); X 16:9 or 1:1, ≤ 2:20; captions go in the post.

## 4. Critique loop (make yourself watch your frames)
Before the full render and after it:
```
ffmpeg -i out/final.mp4 -vf "fps=2,scale=270:-1,tile=6x5" -frames:v 1 out/contact.png      # overview
ffmpeg -ss <t-0.1> -i out/final.mp4 -vf "scale=320:-1,tile=12x1" -frames:v 1 out/strip.png  # 12 frames around a fast move
ffmpeg -i out/final.mp4 -vf "fps=1,scale=360:-1,tile=5x3" -frames:v 1 out/phone.png         # readability at phone width
ffmpeg -stream_loop 1 -i out/final.mp4 -c copy out/loop_check.mp4                            # loop seam (loops only)
```
Score 1–10: hook in the first 2 s · readability at 360 px · motion quality (eased, no dead frames, nothing linear) · variety (something new every 2–4 s) · composition · brand/data accuracy · sound sync. Write **director's notes in camera language**, each naming the element, the move and a number ("title in 6 frames earlier", "push 1.3× slower", "cut on beat 9"). Also tile 16 evenly spaced frames and judge each as a still poster (empty/near-black frames, half-empty vertical frames, proof text too small, text caught mid-reveal). Hunt for: text overlapping during swaps, dead air between scenes, corner labels, blurry scaled text, a dead beat, a loop stutter. Fix, re-render only the affected seconds, re-score. Repeat until every score is 8+. Be a harsh motion director, not a proud author.

## 5. Working with the user's notes
- Apply every note, then tighten what the note implies. Translate vague notes ("more dynamic", "more premium", "WOW") into concrete camera notes and **list them before applying**, so the user sees what changes.
- "Completely different concept" = a new device and structure (DIRECTION.md §3), not more polish.
- Effort: small fixes at medium; a new film at high; the first 3 seconds of a launch deserve max.

## 6. Delivery checklist
☐ stills looked at ☐ critique scores all 8+ ☐ 0 unexplained pops ☐ drop on the key moment ☐ voice intelligible, music ducked (if narrated) ☐ −14 LUFS ☐ TV-range BT.709 ☐ illustrative data labelled ☐ fact-check list written ☐ caption true ☐ MP4 in the working directory, path given, scene table + knobs listed.
