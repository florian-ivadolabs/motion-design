# motion-design

A [Claude Code](https://claude.com/claude-code) skill that directs and builds finished motion-design videos entirely in code: launch films, promos, product demos and tutorials, narrated explainers, logo stings, LinkedIn/X/Reels clips.

The film is one HTML page whose every frame is a pure function of time (`window.seek(t)`). Playwright renders it frame by frame, ffmpeg encodes it, and music, sound effects and voice-over sit on the same clock. No After Effects, no Remotion licence: Chromium, ffmpeg and Python only.

## What the skill does

- **Direction:** research the subject, pick a style reference, sketch three different storyboards, then a beat map.
- **Engine:** springs, camera moves, masked type reveals, transitions, subframe motion blur, any format (16:9, 9:16, 4:5, 1:1).
- **Product screens:** real app captures with Playwright, flipbooks of async states, callouts that never cover what they explain.
- **Sound:** stock music with the drop on the key frame, or a score synthesised in numpy; SFX placed by measured peak; −14 LUFS master.
- **Voice-over:** Gemini TTS (or the keyless macOS `say` fallback), each clip transcribed back and checked word by word; the voice drives the timeline.
- **Critique loop:** contact sheets, phone-width checks and pop scans, scored until every axis is 8+.
- **Remake:** a frame-locked 1:1 remake of a reference video for another brand.

## Install

```bash
git clone https://github.com/florian-ivadolabs/motion-design ~/.claude/skills/motion-design
uv venv ~/.venvs/motion-design
uv pip install --python ~/.venvs/motion-design/bin/python playwright imageio-ffmpeg numpy pillow
~/.venvs/motion-design/bin/python -m playwright install chromium
```

Optional, for voice-over: a Gemini API key in `$GEMINI_API_KEY` or `~/.config/gemini/key`. Without one, the skill falls back to macOS `say`.

Then ask Claude Code for a video, or type `/motion-design <your brief>`.

## Files

| File | Role |
| --- | --- |
| `SKILL.md` | The direction loop, render, gotchas, critique loop, delivery checklist |
| `DIRECTION.md` | Research, style reference, concept and storyboards, beat sheet, taste |
| `DEMO.md` | Films over real product screens |
| `ENGINE.md` | The `seek(t)` engine and its idioms |
| `AUDIO.md` | Music, SFX, synthesised score, loudness |
| `VOICE.md` | Narration pipeline |
| `ASSETS.md` | Free sources for photos, video, logos, icons, fonts |
| `REMAKE.md` | Frame-locked remakes |
| `scripts/` | Film template, renderer, synth, voice and verification, audio, remake tools |

## Credits

A fork of [howseen-ai/claude-motion-design](https://github.com/howseen-ai/claude-motion-design) by Howseen AI (MIT). The engine idea, render, pop-scan and remake scripts and most gotchas are theirs. This fork makes it generic and adds the direction layer, the product-screen craft, the voice pipeline and the synthesised score. See `CHANGES.md`.

MIT licence, see `LICENSE`.
