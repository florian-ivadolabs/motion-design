# Films over real product screens

Craft for any film that shows a real app (demo, walkthrough, tutorial, product promo). These are techniques, not a template: pick what the brief needs.

## Capture (Playwright)
- `device_scale_factor: 2`, a viewport the size of the app you'll show. Drive the real flow and screenshot every state a viewer should see; log `boundingBox()` of anything you'll point at (those are world coordinates).
- Long async work (a build, a run, an upload) reads best as a **flipbook of real states**: a still every 2–3 s while it runs, played back in order. If running it costs money, say so and ask; otherwise use a saved replay and label it.
- Traps: fixed-position UI (drawers, modals) needs a viewport tall enough to hold it, since an element shot of overflowing fixed content grabs the page behind; unpin sticky headers before element shots; reach iframes with `contentFrame()`; set control values and dispatch `input`/`change` to capture widget states.
- Tile the captures into a contact sheet and check them before building.

## Camera and overlays
- Camera `{cx, cy, z}` over the screenshot; zoom in log space; motion blur (SUB 6–8) on fast moves. A hold–whip–hold rhythm (still while the viewer reads, a quick blurred move between regions) often reads cleaner than constant slow drift.
- Draw overlays attached to the product inside the scaled world (callout outlines, tags, cursor targets) with strokes divided by zoom; labels in screen space by projecting world points.
- **An overlay never covers the element it explains**: move the anchor or the tag instead.
- Cursor on eased paths with a small press on click; typing as a string slice at a human speed, one key sound per character.

## Patterns that suit tutorials and walkthroughs (optional)
- The app kept in a device or browser frame, with a text column or lower third for the step, so the viewer always knows they are looking at the product.
- Numbered chapters that follow the user's journey, a small chapter label or progress indicator, and a recap of the steps at the end.
- Focus pulls (blur/darken the rest) for emphasis; callout tags on the real element ("4 KPIs", "Your question").
- A promo or pitch of the same product can instead cut to diagrams, code or title cards to make its argument; choose per brief.
