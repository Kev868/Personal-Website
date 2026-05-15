# Personal Site — Lingfeng Kevin Ge

Single-page hi-fi portfolio. **`index.html` is self-contained** — embedded CSS + inline JS + inline SVG, no build step, no external libraries beyond Google Fonts. Open it directly in a browser. Hosted in Vercel

## What's inside the page

| Section | Anchor | Background | Notes |
|---|---|---|---|
| Hero | top of page | abyss → midnight (+ moonlight shimmer + radial teal/blue) | 5-step staggered fade-up entrance |
| 01 At Anchor — About | `#about` | deep-night → navy | Italic-drop-cap bio paragraphs |
| 02 Currents in Code — Software | `#software` | navy → ocean | 3-column grid · 2 project cards + placeholder |
| 03 Beneath the Surface — Hardware/PCB | `#hardware` | ocean → deep-blue | 2-column grid · 1 PCB card + placeholder |
| 04 Surfacing — Achievements | `#achievements` | sea → deep-blue (BRIGHT) | Inverts to dark text · 6 cards |
| 05 Toolkit — Skills | `#skills` | sea → navy | 4-column skill groups · mono chips |
| 06 Get in Touch — Contact | `#contact` | navy → abyss | Centered, gradient text, 3 glass buttons + footer |

Animated wave divider sits between every section.

## Editable slots (search the file for `***`)
- `*** Card 3 placeholder ***` — Software section, third slot
- `*** Board 02 placeholder ***` — Hardware section, second slot

## Reusable patterns documented in this kit

These are the canonical DOM patterns. Any new section / card should be authored by copying one of these and editing the contents — never by inventing a new shape.

- **`.wave-divider`** — three layered SVG paths, GPU-only translateX loops at 18s/24s-rev/32s. The fill of every path inside one divider must match the *next* section's background color.
- **`.project-card`** — visual on top → mono index → Fraunces title → mono stack → prose → ⚡-bulleted list → mono link with growing arrow.
- **`.pcb-card`** — wider visual on top (radial-glow PCB silhouette) → index → title → mono meta → prose → tag chips.
- **`.ach-card`** — bright surface, dark text, mono badge with glowing teal dot, italic place line.
- **`.skill-chip`** — mono uppercase pill, hover lifts 2px and recolors border + text to electric/bolt.
- **`.pill`** — glass pill (backdrop blur) used in hero + as `.contact-btn`.
- **`.bubble` / `.spark`** — atmosphere primitives. Already provisioned at the top of `<body>`; add more by duplicating the pattern.

## Why no JSX components in this kit
The brief is explicit: *"No build step. No external frameworks beyond Google Fonts."* Splitting into JSX would require React, Babel, or a bundler. The DOM patterns above serve the same purpose — they're documented inline with comment headers in `index.html` (sections 1–18) so each block is locatable and copy-pasteable.
