# Personal Site — Lingfeng Kevin Ge (blend build)

Single-page portfolio. **`index.html` is self-contained** — embedded CSS + inline JS + inline SVG, no build step, no external libraries beyond Google Fonts. Open it directly in a browser, or host statically (Vercel, Netlify, GitHub Pages, etc.).

This build blends two reference portfolios — **wangdynasty.ca** (lowercase casual voice, merged intro, `© year` footer) and **garysun.work** (numbered sections, generous whitespace, CTA hero) — reskinned in a **parchment + Chinese-calligraphy** aesthetic. All prior ("ocean descent" / koi / bubbles) theming was scrapped; only the real content — text, links, images, resume, buttons — was carried over.

## Design system
- **Parchment ground:** warm aged-paper background with a subtle multiplied fractal-noise grain; sepia ink text; **cinnabar seal-red** accent used sparingly (section numbers, links, hover, the small seal square in the intro).
- **Type:** *Ma Shan Zheng* (Chinese brush calligraphy) for the big display headings — the name, section titles, brand, resume name — and *Spectral* (book serif) for all body copy, labels, tags, and content titles.
- The intro (name + about) and every section are single-theme parchment; colors live as CSS custom properties in `:root`.

## Page structure
| Section | Anchor | Notes |
|---|---|---|
| Intro (name + about, merged) | `#top` | seal chip · "hey, i'm" · brush name · role line · bio paragraphs · two CTAs · social icons |
| 01 / Software | `#software` | 3 project cards (image, serif tags, bullets, GitHub link) |
| 02 / Hardware | `#hardware` | Midnight Sun PCB card with 3 board images |
| 03 / Highlights | `#highlights` | 2×2 highlight cards |
| 04 / Skills | `#skills` | 4 grouped chip clusters |
| 05 / Resume | `#resume` | full structured CV + two PDF downloads |
| 06 / Contact | `#contact` | heading, lead, email/LinkedIn/GitHub buttons, footer |

## Behavior (inline JS)
- Nav gains a hairline border once scrolled.
- Scroll-reveal via `IntersectionObserver` (respects `prefers-reduced-motion`).
- Click any project/PCB image (`.zoom`) to open a lightbox; close on backdrop click, the × button, or Escape.

## Assets
- `projects/*.png` — project + PCB screenshots.
- `Kevin(Lingfeng)_GeResumegeneralHardware.pdf`, `Kevin_Lingfeng_GeResumesoftware.pdf` — resume downloads.

## Editing
- Add a project: copy an `<article class="card">` block in the Software section.
- Colors/spacing/fonts: edit the tokens in the `:root` (and the `prefers-color-scheme: light`) block at the top of the `<style>`.
