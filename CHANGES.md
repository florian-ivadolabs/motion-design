# Changes vs upstream (howseen-ai/claude-motion-design, MIT)

Upstream: https://github.com/howseen-ai/claude-motion-design (skill/motion-design). Engine idea, render/pop/remake scripts and most gotchas are upstream's; this fork makes it generic and merges the direction, voice and score parts of the `motion-film` skill.

## Genericity review of upstream (what was author-specific)
- Name/description scoped to "Raphaël / Howseen"; workdir `~/Desktop/Howseen AI/howseen-video/`, venv and ffmpeg paths on the author's machine.
- References to local files that don't ship with the skill: `frame/frame.html`, `reel2/reel2.html`, `h20/h28.html`, `crave/fonts/…`, `promo60/…`, `baguette/…`, `howseen-video/sfx/`.
- Howseen brand palette and product rules (native CMS list, "no Howseen logo in AI images"), house copy rule (no em/en dashes), French lead-magnet banner, dated project log.
- Measured Mixkit track table tied to downloaded files; meme library in a project folder.
- `render_template.py` hard-coded 1080×1350, 24 s, one URL; `audio_template.py` was a Howseen soundtrack; remake `core.js` carried Howseen tokens and a Gojiberry palette filter.
- Voice-over: only a one-line mention of Cartesia (key required, no pipeline, no keyless path).
- Missing direction layer: no research step, no three-storyboard selection, no taste rules (device from the material, one visual system, show-don't-list, text holds), no notes→camera-notes rule, no fact-check list at delivery, no synthesised-score route.

## What this fork changes
- SKILL.md rewritten generic; details split into DIRECTION / ENGINE / AUDIO / VOICE / ASSETS / REMAKE.
- New `scripts/film_template.html`: seek(t) starter (format from `?w&h`, eases, springs, seeded PRNG, masked lines with serif-italic accents, scene table with per-scene roots, portal-dive transition, optional `timeline.json`).
- `render_template.py`: W/H/FPS/SUB/T/BPM/URL from env, duration read from `window.TOTAL`, `full t0 t1` partial renders, BT.709 TV-range encode built in, drafts with `SUB=1`.
- New `scripts/synth.py`: synthesised score toolkit (instruments, SFX, sidechain, reverb, voice ducking, two-pass loudnorm, energy check).
- New `scripts/voice.py`: Gemini TTS or keyless macOS `say`, key discovery without printing, trim, `timeline.json`.
- `audio_template.py` generic (config block + `events.json`, SFX by measured peak).
- Remake engine comments/title de-branded (tokens marked as example values).

## Round 2
- DEMO.md: restores motion-film's "camera over real screens" craft that the merge had dropped (capture traps, flipbooks of async states, world-space overlays, the never-cover rule, motion blur on moves), plus optional tutorial patterns. Guidance, not a template.
- DIRECTION.md §3: lighter concept step (mine the material, diverge, swap and one-sentence tests, three storyboards).
- scripts/verify_voice.py: strict transcript check; voice.py --only; .env inline comments handled.
