# Music, SFX and loudness

Two routes; pick per film and say which:
- **Stock track** (Mixkit, free commercial licence): fastest route to a "real" sounding track. Drop aligned by measurement.
- **Synthesised score** (`scripts/synth.py`): original, offline, licence-free, exactly on the frame grid; best when no track fits, the user names a copyrighted track (compose an original in that style), or every hit must be scored to picture.

## Style → numbers
From a named style, artist or mood, write down **tempo, key/mode, sound palette (sources, bright/dark, clean/distorted), rhythm pattern, arrangement arc (intro, build, drop, breakdown, outro)**. Tempo guide: 60–80 BPM regal, 90–110 smooth, 115–123 elite/sophisticated, > 125 hype. Choose a BPM whose beat is a whole number of frames (30 fps: 120 → 15, 100 → 18, 90 → 20) so scenes land on bars.

## Stock track (scripts/analyze_song.py, audio_template.py)
- Mixkit music: `https://assets.mixkit.co/music/<id>/<id>.mp3`; IDs by grepping `music/[0-9]+/[0-9]+\.mp3` in a listing page. Keep a local table of tracks you measured (id, BPM, drop time).
- **Tempo octave trap**: autocorrelation BPM often reads half or double (60 for a 120 track). Check against the listing's stated BPM and the kick spacing; if the beat grid lands between kicks, double it.
- **Find the drop by energy**, never trust an auto beat grid: per-bar low/full band energy, then 20–50 ms windows around the jump. Start the song at `drop_in_song − drop_in_film`.
- SFX: Mixkit (`https://assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3`, search with `scripts/mixkit_sfx_search.py <tag>`), or synthesise (below).
- **Place every SFX by its measured peak** (`argmax |s|`), gain 0.04–0.3; keystrokes follow the on-screen typing rhythm, one per character.

## Synthesised score (scripts/synth.py)
- Stereo float buses at 44.1/48 kHz: `mix(t, x, gain, pan, send, bus)` onto dry / music / reverb-send buses; one `fs(frame)` helper shared with the picture's frame numbers.
- **Sidechain**: every kick writes a dip into a duck envelope that multiplies the music bus.
- **Reverb**: FFT convolution of the send bus with ~2–3 s of decaying, low-passed noise normalised to unit energy.
- **Blocks**: sine / saw `2((ft+φ) mod 1)−1` / square; detuned stacks for width (supersaw = 7 saws ±1.2 %); envelopes (attack/release, `exp(−kt)`); one-pole low-pass with a moving cutoff (plucks, builds, sweeps; loop only over short notes); pitched percussion `f0(1+a·e^{−kt})` + a noise transient (kick, thud, tom); noise bursts (hats, claps with 3 staggered bursts), swept noise (whoosh, riser, reverse swell), FM bells for pings; choirs/formants for voices.
- **Arrangement**: sections by frame (intro pad + muted pulse → build: snare 8ths → 16ths + riser → drop on the key frame: 4-on-the-floor, offbeat bass, clap 2 & 4, 16th hats, stabs, arp → breakdown under a quiet scene → build → second drop → final chord and tail).
- **Sound on picture**: every visual event gets its sound from the same frame numbers: cuts/dives (reverse swell into a sub thump on the downbeat), landings, chips and dots (blips pitched up a scale), counters (ticks), typing (one tick per character at the typing speed), a pen or clock (tick per edge, on the beat). When a sound acts out the concept, measure it on the audio.
- Check the energy arc per bar (RMS per 2 s): the intro must not be near-silent; the drop must be audibly higher; the breakdown dips.

## Master
Normalise, soft-clip with `tanh`, fade in/out, then **two-pass loudnorm to −14 LUFS** (TP −1). Verify with `ffmpeg -af ebur128`. For "premium/Apple" films: few, soft hits; remove anything loud or out of place.

Mux: `ffmpeg -i out/video.mp4 -i out/audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart out/final.mp4`.
