# Direction: from brief to a film only this subject could have

## 1. Research the subject yourself
- Visit the website, read the docs and decks the user points to. For a **person**: everything public (posts, publications, talks, GitHub, employer pages, Google Scholar). LinkedIn is login-walled: use search snippets, The Org, Scholar, employer bios, or ask the user for screenshots of Experience / About (their own words are gold).
- Fan out research agents when there's a lot of material. Each fact comes back with its source and a confidence (confirmed / likely / uncertain); flag namesakes.
- Collect: real numbers with source, brand colours (read the site CSS), logo vector, fonts (name the closest free match if the brand font is commercial), real product screens.
- If the user gave a braindump of how they see the film, it outranks your ideas. Ask for one line only when the brief is truly ambiguous.

## 2. Style reference
- Use the one the user names. Otherwise browse a curated source (whatships.com, a studio reel, a brand's own launch films) and pick 1–2 pieces that fit subject and audience. Ask before downloading any video; sampling frames in the browser is enough.
- If browsing is blocked or no reference fits (fictional brand), derive the grammar from the brand and the genre's conventions and say so.
- Write `docs/style_guide.md`: palette hex, type (face, weight, scale, placement), shot length and text hold, transition vocabulary, camera, texture. Every later choice traces back to it or to the brand.

## 3. Concept, then three storyboards
- **Where the idea lives depends on the brief**: a promo, teaser or sting usually wants a device (a visual metaphor carried through); a tutorial or walkthrough is usually best told through the product's own flow (DEMO.md). Read the brief, not a rule.
- **Mine the raw material first** and write it down with sources: what the name literally means or sounds like (Tessel → tessellation), the tagline, the subject's own words, the product's core gesture, the defining number, the problem it removes, artefacts of its field (a control loop, an oak ring), the shape of its output.
- **Diverge before choosing**: sketch several candidates quickly. Useful prompts, not a checklist: the name made visible, a material that becomes the mark, the core gesture driving the camera, the problem as antagonist, one object's journey, data as landscape, the UI as a world, the subject's own sentence staged literally.
- **Two quick tests**: the *swap test* (would it still work for a competitor? then it's generic) and the *one-sentence test* (can a stranger repeat it?). Name the motif that carries through.
- **Three storyboards**, genuinely different in device, structure and visual system; each = title, device, 5–8 beats. Show a table with your pick and one line on why each loser lost; continue on the pick unless the user asked to choose. Parallel concept agents are an option when the budget allows.

## 4. Beat sheet
- One row per scene: seconds (on the beat grid, one beat = 1800/BPM frames at 30 fps), what's on screen, **one message**.
- Read it as a viewer with no context: cut redundancy, each fact appears once, energy never sags, text holds long enough.
- **Choose the facts**: a film carries ~1 idea per 3 s. For ≤ 15 s keep the 2–3 strongest proofs; list what you dropped in the delivery so the user can swap.
- **Sell with insights, not a CV**: for promos of people or products, each scene is a claim the viewer cares about + its proof ("Trained where late means broken" + "10 years of embedded control loops"), building one argument (problem → why this subject → proof → call to action).

## 5. Taste
- **One visual system per film**: one motion language carried through (e.g. every transition dives into a dot that becomes the next scene), not a sequence of unrelated effects.- **Show, don't list**: every claim becomes a small scene of it happening (a pen draws the control loop, a lens locks the lesion, dots flow research → production).
- **Readable**: text holds ≥ 2.5 s after its reveal and ~1 s per 3 words; one idea per screen; check at 360 px wide.
- **The look is derived, not defaulted**: palette, type and motion come from the brand and the reference. A flat multi-colour palette = 5–7 hues that belong together (e.g. teal / aqua / orange / saffron / sand / ink), each scene one field, contrast checked for every text colour on every field.
- **Premium motion** = precise eases (quint/expo, no overshoot), whole-line mask reveals, a serif-italic accent word in a tight sans, continuous camera; "cheap" = bouncing letters, per-letter pops, random effects.
- **Built in code**: graphics and type made in the page; photos only when supplied or the concept needs them; product films use real screenshots. UI that isn't captured is built from real components (21st.dev, shadcn/ui, the brand's library) ported to `seek(t)`.
- **Proof points readable, not just headlines**: as a guide at 1080 px on the short side, body text around 36 px and labels around 28 px; push the camera in on UI details that carry the point.
- **Scan 16 evenly spaced frames**: empty or half-filled frames, text caught mid-reveal, or an end state held for a large share of the runtime usually signal a pacing or framing problem.
- **The first frame is the thumbnail**: never empty or black (feeds autoplay muted and show frame 0); burn in the key words, since most viewers watch without sound.
- **Short forms**: logo sting (5–10 s) = one gesture that builds the mark, a lockup that holds ≥ 1.5 s, optional tagline, clean tail; 15 s clips = 4–5 ideas max, relax the 2.5 s text hold only for 1–2-word punches.
- **Characters only on request.**
- **Locked to the music**: cuts, landings and reveals fall on the beat grid.
- **Craft over effects**: depth from parallax, perspective, motion blur and light; effects don't rescue a weak concept.

## 6. Notes, iterations, delivery
- Apply every note; translate vague ones into listed camera notes first. "Completely different concept" = new device + new structure.
- Deliver: the MP4 in the working directory (send it), a scene table (time · on screen · message), the **fact-check list** (every figure, its source, anything the user must confirm: derived numbers, positioning claims, clearances), and the cheap knobs (length cut, a line of copy, format 9:16/4:5/1:1, music style/tempo, voice).
- Offer the obvious next formats (vertical for LinkedIn/Reels, a 30 s cut) in one line.
