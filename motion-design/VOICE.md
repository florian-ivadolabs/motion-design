# Narrated films

The voice drives the timeline: write the script, generate and measure every line, then build the picture to fit `timeline.json`.

## The key: find it, else ask where it is (never in chat)
`scripts/voice.py` looks, without printing any value, in: `$GEMINI_API_KEY`, `~/.config/gemini/key` (bare key), `./.env` or `../.env` (`GEMINI_API_KEY=…`). Check presence yourself only by name (`test -s ~/.config/gemini/key`, `grep -c '^GEMINI_API_KEY=' .env`).

If none is found, **don't block and don't fall back silently**: write the script and start the picture, and ask once (AskUserQuestion), with "It's in a file" first as the recommended option:
- **"It's in a file"**: they give the path; if it is a `.env`, run voice.py from that folder, else copy the key to `~/.config/gemini/key` (chmod 600) without printing it.
- **"Set it up"**: give them the one-liner to run themselves: `mkdir -p ~/.config/gemini && printf '%s' 'YOUR_KEY' > ~/.config/gemini/key && chmod 600 ~/.config/gemini/key` (AI Studio → Get API key; free tier).
- **"No key: macOS voice"**: `--engine say` (keyless, lower quality; the script picks an Enhanced/Premium English voice if installed, else Samantha). Suggest installing an Enhanced voice (System Settings → Accessibility → Spoken Content) for a big quality jump.
- **"No voice"**: subtitles + music only.
Never ask for the key in chat. If it's pasted anyway, write it to `~/.config/gemini/key` (chmod 600) and tell the user to rotate it. When running autonomously with no user, use `say` and state it plainly in the delivery ("voice: macOS say, lower quality; a Gemini key gives a far better voice").
Other engines (Cartesia, ElevenLabs, OpenAI TTS) work the same way if the user has a key: one clip per line, then the same trim + timeline step.

## Pipeline (scripts/voice.py)
1. **Script** `script.json = [["chapter", "line"], …]`. Write for the ear: short clauses, one idea per line, numbers spelled as spoken ("seven hundred", "twenty twenty-six"). Name chapters as actions for the viewer; end on a recap or call to action.
2. **TTS** (`python voice.py script.json --voice Kore`; the default engine is `gemini` and stops if no key is found, `--engine say` only once the user chose it): Gemini lists models and picks the newest flash TTS; 4 lines in parallel with retries. Traps handled: newer models return a full RIFF WAV (written as is), older raw 24 kHz L16 (header added); a style prefix like "Say calmly:" is **read aloud**, so send the plain line only. Pick a prebuilt voice to match tone and audience and tell the user which one so they can swap.
3. **Verify** (Gemini only): `python verify_voice.py timeline.json` transcribes each clip back and flags every substituted word after normalising numbers; regenerate failures with `voice.py --only <i>`. Loose matching misses real errors ("feature" heard as "future"). With `say`, listen to 2–3 lines instead (or check durations are plausible: ~2.5–3 words/s).
4. **Trim & time** (done by the script): silence stripped both ends; first line at 1.2 s, 0.45 s between lines, +0.9 s at a chapter change, 2.5 s tail → `timeline.json = {lines:[{i,ch,text,start,dur,file}], total, engine, voice}`.

## Hitting a fixed length
The spacing constants eat time (a 20 s film with 5 lines loses ~7 s to lead-in, gaps and tail). Flex in this order: cut copy (≈ 2.7 words/s of voice), raise the speaking rate ≤ 10 %, shrink gaps to 0.3 s and chapter pauses to 0.6 s, tail to 1.5 s. Never speed-change the rendered audio.

## Checking a voice nobody can listen to (autonomous runs)
Gemini: transcribe each clip back. `say`: check each clip's duration is 0.3–0.45 s per word and that `silencedetect` pauses fall at clause boundaries; spell initialisms for the engine ("M L") while subtitles keep "ML".

## Picture from the timeline
- `film_template.html` fetches `timeline.json` (`TL`) and exposes `currentLine(t)` = last line with `start − 0.15 ≤ t`. Set scene durations from the timeline (a scene per chapter or per line), not the other way round. `window.TOTAL = TL.total`.
- Each line's shot is a function of `lt = t − line.start`; land its visual event while the words are spoken, early rather than late.
- Reserve a **subtitle band** nothing important enters; show the current line from 0.1 s before its start to 0.2 s after its end; show chapter + progress. Burned subtitles are expected on LinkedIn (autoplay is muted).
- Keep the music grid: snap chapter starts to the nearest beat by nudging the gaps (±0.2 s), not the speech.

## Mix (scripts/synth.py → Score.voice / duck_under_voice)
Resample clips to the score rate, place each at its `start` on the dry bus (peak ~0.92), build a speaking mask, smooth it with two 0.25 s box filters and multiply the music bus by `1 − 0.65·mask` (≈ 9 dB duck). Music master ~0.28 of the voice peak. Target about −15 dB mean on the voice and −23 dB in the gaps (`ffmpeg -af volumedetect`), then the master loudnorm to −14 LUFS.
