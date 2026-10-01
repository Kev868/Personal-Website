# Asset brief: painting the palace

Everything on the site is drawn in code right now: the roofs, pillars, doors,
lanterns and clouds are stand-ins. They work, but painted layers in the style of
the banner (`assets/img/bannertouse.png`) will make it feel like one painting.
This is how to make them in ChatGPT's image generator, and where each one goes.

## How to ask

1. **Attach the banner** to every request as the style reference.
2. **End every prompt with the same style sentence**, word for word:

   > Chinese ink-wash painting on aged rice paper, soft misty gradients, delicate
   > brushwork, muted palette with accents of vermilion lacquer and burnished
   > gold, soft light from the upper left, same style as the attached image.

3. **One object per image, on a transparent background.** Add:

   > Transparent background (PNG). The whole object visible with some margin
   > around it. No text, no people, no shadow on the ground.

   If it comes back with a background anyway, ask again for a flat solid green
   (#00FF00) background instead. Send the file either way; cutting it out is my
   job, not yours.

4. **Ask for the landscape size** (1536×1024) for anything wide and the
   portrait size (1024×1536) for anything tall. Those are the largest ChatGPT
   makes; for the widest pieces, two overlapping halves are better than one
   stretched image.

## The pieces

The architecture stays drawn in code: roofs, pillars, doors and plaques have to
line up to the pixel (the pillars stand under the ends of the roof's bracket
band, the lanterns hang from it), and a painting cannot be made to. What
paintings do better is atmosphere: the clouds and the far distance. In order of
impact:

| # | Piece | Size | Replaces | Prompt (before the style sentence) |
|---|---|---|---|---|
| 1 | Cloud banks, 3 versions | landscape | the clouds between every scene | A long horizontal bank of soft billowing cumulus clouds seen from the side, stretching the full width of the image, its top edge rising and falling in soft domes, its underside flat and fading into mist. Nothing else in the image |
| 2 | Cloud clump, 2 versions | landscape | the clouds that the distant towers and the gate's pillars stand in | A single small clump of soft billowing cloud, wider than it is tall, domed in the middle and tapering at both ends, its underside dissolving into mist, centred with plenty of empty space around it |
| 3 | Cloud wall, 1 | portrait | the clouds that roll in when you travel | A tall dense wall of soft white cloud filling the left two-thirds of the image completely, with its right edge breaking into large rounded billows. The right third is empty |
| 4 | Far heavens | landscape | the distant towers behind everything | A distant sea of clouds at the bottom of the image with three small, faint palace pagodas rising out of it at different distances, their bases hidden in the cloud, the upper two-thirds of the image empty sky. Very faded and hazy, low contrast |
| 5 | Bell tower at night | portrait | the tower at the bottom of the page | A three-tiered Chinese bell tower rising out of a bank of clouds at night, its base hidden in the cloud, windows glowing warm gold, seen from the front, dark blue-violet silhouette |
| 6 | Hall interior | landscape | the backdrop inside each project hall | The inside of an imperial Chinese palace hall seen from the doorway: red lacquered pillars receding in two rows, a painted coffered ceiling, gilded screens at the far end, warm lamplight, dark and rich. On plain background, not transparent |
| 7 | Lantern, 1 | portrait | every lantern (optional) | A single red silk palace lantern with gold caps and a red tassel, hanging from a short cord at the very top of the image, glowing softly from inside, front view |

The first five are in (`assets/img/`, prepared into `assets/art/` by
`tools/prepare_art.py`):

| Painting | Where it is |
|---|---|
| `Cloudswide1-3.png` | the cloud banks at the gate's foot, between the halls, and over the library |
| `Cloud1.png`, `Cloud2.png` | at the gate pillars' feet, and floating over the bridge between the halls |
| `Cloudwall.png` | the travel transition, widened into one wall |
| `Farheavens.png` | the distant towers behind everything, faded for distance |
| `Belltower.png` | not shown for now (prepared as `assets/art/bell-tower.webp`, ready to come back) |

To replace one, save over it with the same name and run the script.

## Sound

Put the files in `assets/audio/` and list them in `assets/audio/manifest.json`:

```json
{ "ambient": "ambient.mp3", "whoosh": "whoosh.mp3" }
```

The Sound button appears in the nav once an ambient track is listed. Good
sources, free with no credit needed (Pixabay Content License):

- Music: search Pixabay for "guzheng" or "guqin". Pick something slow, with no
  drums, one to three minutes long, that loops without a bump.
- Whoosh: search Pixabay sound effects for "cloud woosh" or "wind whoosh".
  Soft and airy, under a second and a half.
