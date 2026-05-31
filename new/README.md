# Andre AI — Interactive Session (`_new/`)

A self-contained, single-file page (`index.html`) — the exact "Interactive
Session" template (glassmorphism, JetBrains Mono, brand purple `#8854F3` /
orange `#F97316`, Tailwind + Font Awesome from CDN), same pattern as the live
`andre.technology` site.

## The idea

The **talking head fills the whole screen as the background** (like the live
site's `assistant-video`). Glass content + nav sit on top.

When you click a nav tab (or a CTA):

- the **head stays** as the full-screen background;
- it smoothly crossfades to that section's **head "part"** — a short trimmed
  slice of the *same* head video, so "the next part speaks";
- that section's panel + **buttons change**.

The mic button un-mutes the background head so it actually speaks out loud.

> Only the head video (`Andre_AI (1).mp4`) is used — nothing else from the repo.

### Layout

- The head video is square (480×480). **On mobile** a **blurred, zoomed copy**
  of the same head (`#assistant-bg`) fills behind the sharp head so it covers
  the whole screen.
- **Desktop (≥1024px):** the head is a **tall portrait rectangle on the left**
  (`object-cover`, `lg:w-[34%]`) whose right edge **feathers into the black**
  background, with the **Andre AI + mic** badge **just below it**. The full
  section menu is **horizontal at the top** and **AI Business OS** is the
  right-most control. Section content lives in the **right area**, centred, with
  **uniform-size cards**: **2–3 cards → one column, 4+ → two columns** (via a
  `:has(> :nth-child(4))` quantity query). Tune the head with the video's
  `lg:w-[…]` / `lg:object-[…]` and the right-edge fade in the
  `@media (min-width:1024px) #assistant-video` mask.
- **Mobile (<1024px):** logo + speaker (Andre AI) + **mic** at the top; on the
  right a **menu button** then the **OS** button (right-most). The menu opens as
  a **full-screen** overlay. Section content sits at the bottom as a **one-card
  swipe carousel**.

## Why it's cut into parts ("обрезать каждую чтобы быстрее загружать")

The 18-second head video is split into **6 short parts** (one per section,
in nav order), each ~140 KB:

| Section | Head part |
|---|---|
| Overview | `assets/head-overview.mp4` (0–3 s) |
| Strategy | `assets/head-strategy.mp4` (3–6 s) |
| Platform | `assets/head-platform.mp4` (6–9 s) |
| Employees | `assets/head-employees.mp4` (9–12 s) |
| Products | `assets/head-products.mp4` (12–15 s) |
| Education | `assets/head-education.mp4` (15–18 s) |

So only ~140 KB loads up front (instead of the whole clip); the rest are
prefetched on tab hover. Walking Overview → … → Education plays the monologue
start-to-finish, one piece per step. Each part has a JPEG poster for instant
first paint.

Want one continuous looping head instead of per-section parts? Point every
entry in `HEAD_PARTS` at the same file — no other change needed.

## Regenerate the parts (needs `ffmpeg`)

```bash
IN="Andre_AI (1).mp4"; i=0
for id in overview strategy platform employees products education; do
  ffmpeg -y -ss $((i*3)) -t 3.2 -i "$IN" \
    -vf "scale=480:480:force_original_aspect_ratio=increase,crop=480:480,fps=25" \
    -c:v libx264 -crf 28 -preset veryfast -pix_fmt yuv420p \
    -c:a aac -b:a 96k -movflags +faststart "_new/assets/head-$id.mp4"
  i=$((i+1))
done
```

## Files

```
_new/
├── index.html            ← the page (open / deploy this)
├── assets/               ← 6 head parts + 6 posters (~0.9 MB total)
├── tests/page.test.mjs   ← jsdom behaviour tests
├── package.json
└── README.md
```

Tailwind / Font Awesome / Google Fonts load from their CDNs at runtime (same as
the rest of the site), so it works as a plain static file on GitHub Pages with
no build step.

## Tests (TDD)

```bash
cd _new && npm install && npm test
```

They assert, among other things:

- the talking head is the **full-screen background** (`#assistant-video` in a
  `fixed inset-0 z-0` layer, `object-cover`, looping/muted/autoplay) — a guard
  so it never regresses to a small avatar
- a `HEAD_PARTS` map covering every section, all `assets/head-*.mp4`
- `openTab(id)` activates exactly that section and points the head at its part
  (`#assistant-video[data-part]`)
- the head element is **never swapped out** (same node) — голова остаётся
- nav tabs and the hero CTA drive the switch; mic toggles mute
- the mobile menu button opens the nav dropdown and closes on navigation
- nav and the OS button stay siblings (no overlap/unclickable-tab regression)

## Customising

Everything lives in the inline `<script>`: `HEAD_PARTS` (section → head clip)
and `HEAD_POSTERS` (section → poster). Add a section by adding a nav tab
(`data-target="x"`), a `<div id="x" class="content-section …">` panel, and `x`
entries in those two maps.
