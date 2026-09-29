# The seek(t) engine

Start from `scripts/film_template.html` (stage, helpers, masked lines, spring, seeded PRNG, portal dive, optional `timeline.json` for narration). One HTML file per film.

## Contract
- Everything is computed from time inside `window.seek = async (t) => {…}`. **No CSS transitions, no timers, no state carried between frames**, no `Math.random` (use the seeded `mulberry32`). Rendering the same second twice gives identical frames.
- Declare all constants and build the DOM once, before the first `seek()`. Set `window.ready = true` after `document.fonts.ready`, image decodes and video `seeked`.
- The render script screenshots `#stage` at the video size; the stage size = the format (`W`,`H` read from the URL query in the template, so one file can render several formats).
- `z-index` on every layer; `visibility:inherit` (not `visible`) for children of hidden parents.

## Timing
- A **scene table** `[{id, start, dur, bg}]` and local time `lt = t - start`: retiming the film is a one-place edit. All starts on the beat grid.
- Every animated property = `lerp(a, b, ease(seg(lt, t0, t1)))`. Eases: `io` (cubic in-out), `out`, `in`, `o5` (quint out), `expo`. Linear motion only for constant flows (marquees, conveyor dots, a pen at constant speed locked to the beat).
- **Springs** = closed-form step response `step(tau, f, z)`; many targets = sum of one spring per change. Presets (freq, damping): snappy UI 3.2/0.9, containers/camera 2.2/0.8, heavy type 1.8/0.85, playful 2.6/0.45. Premium films: no visible overshoot on type.

## Camera
- One transform on a container: world point `(cx, cy)` sits at screen `(sx, sy)` at zoom `z` → `translate(sx,sy) scale(z) translate(-cx,-cy)`. Keys `[t, z, x, y]`, eased segments, **zoom interpolated in log space**, never zoom in and out back to back.
- Beat punches: +0.012 scale per beat, +0.03 per bar after the drop, exponential decay. Only during high-energy sections.

## Type
- **Masked line rise**: each line in an `overflow:hidden` box, inner `translateY(110% → 0)` with `o5` over ~20 frames, 3–5 frame stagger between lines; exit is the same upward. Word-by-word (55 ms stagger, tiny rotation) for playful films; whole lines for premium.
- Accent words: a serif italic inside a tight grotesk (e.g. Instrument Serif italic + Inter Tight 600, tracking −0.035 em), or a moving gradient via `background-clip:text`.
- Break headlines by hand (`|`) so no line leaves an orphan; measure with canvas `measureText` when you need positions (e.g. to place a dot after the last glyph).

## Transitions (one vocabulary per film)
- **Flood**: a circle grows from the source object until it clears the farthest corner (`hypot` to 4 corners × 1.05) in ~0.3–0.35 s, then contracts into the next object.
- **Portal dive** (continuous single take): each scene owns a "portal" dot coloured as the *next* scene's background (the period of a name, a pen tip, a lens centre, a cursor). In the last beat, the camera pushes into it (`scale = 6^(in4(p))` around the dot) while the dot's radius grows to cover the frame; the next scene arrives from 0.86→1 scale with `o5`. The whole film reads as one take.
- **Shared elements** for handoffs (a bubble carries its words into the flood, a button its label into the page). Text that swaps inside a morphing shape gets its own mask.
- Panel wipes / hard cuts on downbeats for high-energy promos.

## Effects library (port ideas, never run live libraries)
Liquid glass (canvas displacement), goo (SVG blur + threshold), 6-blade iris, variable-font width squeeze, 3D cube (CSS 3D), equalizer, blob mask, dotted grid, drifting blobs, sheen sweep, sparkles, Animated Beam / Border Beam (21st.dev ideas), orbiting circles, square-wave pen, rotating dashed rings, bar charts that rise on the beat, multiply-blend Venn with a clipped core.
Seekable libraries are fine: Anime.js (`autoplay:false`, `anim.seek(ms)`), Theatre.js (`sheet.sequence.position = t`). Never Spline/Unicorn/framer-motion live: they can't be seeked.

## Traps
- SVG glow filters on thin or axis-aligned lines vanish (zero-width bounding box): use `filterUnits="userSpaceOnUse"` with explicit x/y/width/height.
- SVG blur on a tiny shape renders as a square (filter region clipped): enlarge the filter region (`x=-200% y=-200% width=500% height=500%`) or use a radial gradient instead.
- Large blurred layers are slow in Chromium screenshots: blur small copies and scale them up, or bake glows into PNGs.

## Formats
Write scenes against a layout function of `(W, H)` and render 16:9, 9:16, 4:5, 1:1 from the same timeline, **re-laying out type and UI per format (never crop)**: vertical = stacked lines, larger type, pipelines that run top to bottom, key content between ~8 % and ~85 % of the height.

## Product screens
Films over real screens: see DEMO.md (capture, flipbooks, overlays in world space).

## Honesty in UI
Real UI = captured screenshots with a camera over them (log positions with `boundingBox()` in Playwright: those are world coordinates). Built UI = real components ported to seek(t); illustrative data labelled on screen.
