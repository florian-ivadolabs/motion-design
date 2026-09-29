# Assets (free sources only, always vetted on a contact sheet)

Default: build graphics and type in code. Use outside assets only when the user supplies them or the concept needs them, and record each asset's source and licence in `ASSETS_USED.md`.

## Photos
- Unsplash: `https://unsplash.com/napi/search/photos?query=…&per_page=30` (curl ok) → `urls.raw + &w=2600&q=85&fm=jpg`.
- Pexels CDN: `https://images.pexels.com/photos/<ID>/pexels-photo-<ID>.jpeg?auto=compress&cs=tinysrgb&w=1600` (search pages block curl; find IDs with WebSearch/WebFetch).
- Build a contact sheet and **look at it** before use. Cutouts from dark backgrounds: luminance + warmth alpha, keep the largest component, trim ~5 px.

## Video
Mixkit `assets.mixkit.co/videos/<ID>/<ID>-1080.mp4`, Pexels `pexels.com/download/video/<id>/`. Re-encode all-intra (`-g 1`) so seeking is exact, load as a blob URL, `await` the `seeked` event inside `seek(t)`.

## Logos & icons
- `scripts/svgl_logos.py <name>` (svgl.app API, colour SVGs of common brands); fallback simple-icons `https://cdn.jsdelivr.net/npm/simple-icons@13/icons/<name>.svg`.
- The subject's own logo: read it from their site (inline SVG / `<symbol>` in the HTML) or ask for the file. Third-party logos only with a reason (e.g. "works with" lists the user confirms), never implying a partnership.
- 3D icons: 3dicons.co (CC0).

## Fonts
Google Fonts / OFL (Inter Tight, Instrument Serif, Geist, Archivo variable for width squeezes, JetBrains Mono…). If the brand font is commercial, use the closest free match and say so. Self-host the woff2 in `fonts/` for fully offline renders.

## Components & effects
- 21st.dev (Magic MCP if installed, else `scripts/mcp21_client.py` with a key in `$API_KEY_21ST` or `~/.config/21st.key`; free tier is rate-limited), shadcn/ui, Magic UI, Aceternity, Motion Primitives: copy the source for exact spacing, then **port the motion to seek(t)**; never run framer-motion or other real-time animation live.
- Ideas to port: Kinetics (kinetics.colorion.co), CSS Text Effects (text-effects.colorion.co), Liquid Glass (glass.samasante.com).

## Music & SFX
See AUDIO.md (Mixkit music and SFX, or synthesised with `scripts/synth.py`).

## Reference and meme clips
Only on explicit request, only for commentary/parody formats, and ask before downloading any video. yt-dlp with `ffmpeg_location=imageio_ffmpeg.get_ffmpeg_exe()`; check a contact sheet for burned-in captions, watermarks and end cards; re-encode H.264 + AAC + `setsar=1`.
