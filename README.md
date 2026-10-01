# kevinge.com: the palace in the clouds

The redesign of the parchment site. The page is a walk along a palace's central
axis, set in the heavens: the Southern Heavenly Gate, a pair of doors, the
software and hardware halls, the library and the bell tower. The sky behind it
moves through one day as you scroll.

## Run it

It is a static site with no build step, but it uses JavaScript modules, which
browsers will not load from a plain file. Serve the folder instead:

```bash
python -m http.server 5510
```

and open <http://localhost:5510/>.

- `?type=b`, `?type=c` or `?type=today` previews the other typeface pairings.
- The arrival (the seal and the parting clouds) plays once per browser tab.
- `#/hall/retask` (or any project key) opens straight into that project's hall.

## Where things are

```
index.html          every scene, every project hall (<template id="tpl-KEY">)
css/palace.css      the whole look, in numbered sections
js/main.js          wires the modules together
js/sky.js           the time of day for each scene
js/scenes.js        the gate's entrance, the doors into the software hall, parallax
js/works.js         the seal filters, Gallery and Register views
js/room.js          project halls and their addresses
js/library.js       the résumé handscroll
js/travel.js        the clouds that roll in and part
js/ui.js            arrival, cursor, lightbox
js/sound.js         optional sound, from assets/audio/manifest.json
assets/img/         the seal and banner; the original paintings are kept out of the repo
assets/art/         the paintings as the site loads them (tools/prepare_art.py)
assets/gen/         drawn-in-code art: the ceiling medallion (tools/generate_assets.py)
tools/build_roof.py the tiled roof every building shares; writes it into index.html
tools/build_scroll.py the closed handscroll in the library; writes it into index.html
tools/build_textures.py the weathering laid over pillars, doors, plaques and paintwork
docs/ASSET-BRIEF.md how the paintings were made, and how to make more
```

## Adding a project

1. Add a card to the right hall's `<ol class="works">` in `index.html`, with a
   link to `#/hall/KEY` and `data-cats` for the seal filters.
2. Add a `<template id="tpl-KEY" data-title="…" data-wing="east|west">` with
   its write-up. The existing ones show the shape.

Previous and next inside the halls follow the order of the cards on the page.

## Replacing a painting

The original paintings are not in the repo (see `.gitignore`): keep them in
`assets/img/` locally. Save the new PNG over the old one there (same name),
then run `python tools/prepare_art.py`. It trims the empty margins, sizes the piece and
writes the WebP the site loads into `assets/art/`. The cloud wall for the
travel transition is built from `Cloudwall.png` there too; a new wall should
keep the old one's shape: portrait, solid across its left two-fifths.

## Reduced motion

With the system's reduce-motion setting on, nothing moves on its own: there are
no doors to open (the software hall simply stands there), travel becomes a
fade, and the arrival is skipped.
