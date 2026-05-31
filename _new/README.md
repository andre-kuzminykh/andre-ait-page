# Andre AI — Interactive Session (`_new/`)

A self-contained, single-file landing page (`index.html`) built in the same
visual language as the existing site (glassmorphism, JetBrains Mono, brand
purple `#8854F3` / orange `#F97316`, Tailwind + Font Awesome from CDN).

## The idea

A **talking-head presenter that stays on screen** while the **cinematic
background scene switches per section** and the **glass content / buttons
morph in**:

- You land on **Overview** — the presenter (Andre AI, the host) greets you and
  the "Andre AI Technologies" gate plays behind.
- Tap a nav tab (or a CTA) → the **head stays put**, the background crossfades
  to that section's "world", a caption under the head updates, and that
  section's panel + buttons animate in — all in the same style.
- The mic button un-mutes the presenter so the head actually *speaks*.

This is the "голова остаётся, следующее говорит, кнопки меняются" behaviour
from the brief.

> **Note on the reference clip.** The reference video mentioned in the brief
> wasn't available in this environment, so the scene⇄section mapping below is a
> best-effort interpretation. It's all data-driven and trivial to re-map — see
> *Customising* below.

## Files

```
_new/
├── index.html            ← the page (open this / deploy this)
├── assets/               ← optimised, web-ready media (5.6 MB total)
│   ├── presenter.mp4      (talking head, with audio)
│   ├── scene-*.mp4        (6 muted background loops)
│   └── poster-*.jpg       (instant first-paint posters)
├── tests/page.test.mjs   ← jsdom behaviour tests
├── package.json
└── README.md
```

The page also loads Tailwind, Font Awesome and Google Fonts from their CDNs at
runtime (same as the rest of the site), so it works as a plain static file on
GitHub Pages with no build step.

## Section ⇄ scene mapping

| Section    | Background scene (source)              |
|------------|----------------------------------------|
| Overview   | Andre AI Technologies gate (`1.mp4`)   |
| Strategy   | Genesis core (`5.mp4`)                 |
| Platform   | Human Intelligence Platform (`3.mp4`)  |
| Employees  | Dataism Science Hub (`4.mp4`)          |
| Products   | Neuronium AI dome (`2.mp4`)            |
| Education  | AI Academy tower (`6.mp4`)             |

## Asset pipeline (why it loads fast)

The originals in the repo root are ~100 MB of 1920×1080 clips. For the page they
were trimmed and compressed with ffmpeg to short, muted, web-optimised loops:

- backgrounds: 5 s, 1280×720, H.264 CRF 31, **no audio**, `+faststart`
- presenter: 480×480, H.264 CRF 30, AAC audio kept (so it can speak)
- a JPEG poster per clip for instant first paint
- backgrounds use `preload="none"` + are prefetched on tab hover; only the
  Overview scene and the presenter load up front

Result: **5.6 MB** for the whole experience instead of ~100 MB.

To regenerate (requires `ffmpeg`), re-run the equivalent of:

```bash
# background (repeat per scene, -an = drop audio)
ffmpeg -y -ss 0 -t 5 -i SOURCE.mp4 -an \
  -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=24" \
  -c:v libx264 -crf 31 -preset veryfast -pix_fmt yuv420p -movflags +faststart \
  assets/scene-NAME.mp4

# presenter (keep audio)
ffmpeg -y -i "Andre_AI (1).mp4" \
  -vf "scale=480:480:force_original_aspect_ratio=increase,crop=480:480,fps=25" \
  -c:v libx264 -crf 30 -pix_fmt yuv420p -c:a aac -b:a 96k -movflags +faststart \
  assets/presenter.mp4
```

## Tests (TDD)

The interactive contract is covered by jsdom tests so refactors can't silently
break navigation, the persistent head, or the audio toggle.

```bash
cd _new
npm install     # one dev dependency: jsdom
npm test
```

They assert, among other things:

- a `SCENES` map covering every section, all under `assets/`
- exactly one active nav tab + section at all times (invariant sweep)
- each `openTab(id)` activates the matching section **and** its scene
- the **talking-head presenter is never swapped out** across navigation
- nav tabs **and** any `[data-target]` CTA drive the switch (event delegation)
- the mic toggle (un)mutes the presenter and updates the indicator
- the fixed top bar is `pointer-events-none` but every interactive group
  (logo / OS button / nav) re-enables them — a regression guard for an
  overlap bug where the OS button covered the last nav tab

## Customising

Everything lives in the inline `<script>` at the bottom of `index.html`:

- `SCENES`         — section id → background video path
- `POSTERS`        — section id → poster image path
- `SCENE_CAPTIONS` — the line shown under the presenter per section

Add a section by adding a nav tab (`data-target="x"`), a
`<div id="x" class="content-section …">` panel, and `x` entries in those three
maps.
