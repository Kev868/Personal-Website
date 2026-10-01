"""The painted layers: from the image generator's PNGs to what the site loads.

The paintings (made in ChatGPT's image generator, see docs/ASSET-BRIEF.md) are
kept as they came, in assets/img/. This trims their empty margins, so that
their edges are the painting's edges and the stylesheet can place them, scales
each to the largest size the site shows it at, and saves WebP with alpha into
assets/art/. Run it again after replacing a painting:

    python tools/prepare_art.py

Needs numpy and opencv-python.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "img"
OUT = ROOT / "assets" / "art"

# source: (output, widest it is shown, in image pixels; trim the margins?)
PIECES = {
    "Cloudswide1.png": ("bank-1.webp", 2200, True),
    "Cloudswide2.png": ("bank-2.webp", 2200, True),
    "Cloudswide3.png": ("bank-3.webp", 2200, True),
    "Cloud1.png": ("clump-1.webp", 1400, True),
    "Cloud2.png": ("clump-2.webp", 1400, True),
    "Farheavens.png": ("far-heavens.webp", 1800, True),
    "Belltower.png": ("bell-tower.webp", 820, True),
}
# Cloudwall.png becomes cloud-wall-wide.webp instead: see wide_wall().


def trim(img: np.ndarray, pad: int = 6) -> np.ndarray:
    """Crop to the painted area, plus a few pixels so soft edges are kept."""
    ys, xs = np.where(img[..., 3] > 4)
    h, w = img.shape[:2]
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + pad + 1)
    return img[y0:y1, x0:x1]


def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def wide_wall(wall: np.ndarray, copies: int = 5, step: float = 0.4, height: int = 1280) -> np.ndarray:
    """One wall of cloud wide enough for any screen, from the 2:3 painting.

    The painting is solid across its left 42% and billows beyond, so it is
    laid down several times, each copy `step` of its width left of the one
    after it and beneath it: only the rightmost copy's billows show. Each
    copy's left edge is feathered into the one below, and the copies ride at
    different heights, so neither the seams nor the repetition read as a
    pattern. A cream ground under the solid part fills what the shifted
    copies leave open at top and bottom.
    """
    h0, w0 = wall.shape[:2]
    scale = height / h0
    tile = cv2.resize(wall, (round(w0 * scale), height), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    th, tw = tile.shape[:2]
    shift = round(tw * step)
    width = tw + shift * (copies - 1)
    canvas = np.zeros((th, width, 4), np.float32)          # premultiplied
    # The ground: the painting's lit cream, fading out well inside the top
    # copy's solid part so it can never show through a notch in it.
    cream = np.percentile(tile[tile[..., 3] > 0.98][:, :3], 75, axis=0)
    xs = np.arange(width, dtype=np.float32)
    ground = smoothstep(width - tw * 0.6, width - tw * 0.75, xs)[None, :].repeat(th, 0)
    canvas[..., :3] = cream * ground[..., None]
    canvas[..., 3] = ground

    feather = smoothstep(0.0, 0.16, np.linspace(0, 1, tw, dtype=np.float32))[None, :]
    lifts = [0.0, -0.07, 0.05, -0.04, 0.08, -0.06][:copies][::-1]   # leftmost first
    for i, lift in enumerate(lifts):
        x0 = shift * i
        dy = round(th * lift)
        layer = np.zeros((th, tw, 4), np.float32)
        src = tile[max(0, -dy): th - max(0, dy)]
        layer[max(0, dy): max(0, dy) + src.shape[0]] = src
        a = layer[..., 3]
        if i > 0:                                  # the leftmost has nothing under it to blend into
            a = a * feather
        if lift:                                   # a shifted copy fades at the edge it was moved off
            ys = np.linspace(0, 1, th, dtype=np.float32)[:, None]
            a = a * (smoothstep(0.0, 0.1, ys) * smoothstep(1.0, 0.9, ys))
        region = canvas[:, x0: x0 + tw]
        region[..., :3] = layer[..., :3] * a[..., None] + region[..., :3] * (1 - a[..., None])
        region[..., 3] = a + region[..., 3] * (1 - a)
    out = canvas.copy()
    alpha = np.clip(out[..., 3:], 1e-4, 1)
    out[..., :3] = np.where(out[..., 3:] > 1e-4, out[..., :3] / alpha, 0)
    return np.clip(out * 255, 0, 255).astype(np.uint8)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    wall = cv2.imread(str(SRC / "Cloudwall.png"), cv2.IMREAD_UNCHANGED)
    if wall is not None:
        wide = wide_wall(wall)
        path = OUT / "cloud-wall-wide.webp"
        assert cv2.imwrite(str(path), wide, [cv2.IMWRITE_WEBP_QUALITY, 80]), path
        print(f"  Cloudwall.png    -> {path.name:22} {wide.shape[1]}x{wide.shape[0]}  {path.stat().st_size // 1024} KB")
    for name, (out, widest, crop) in PIECES.items():
        img = cv2.imread(str(SRC / name), cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"  missing {name}, skipped")
            continue
        assert img.ndim == 3 and img.shape[2] == 4, f"{name} has no transparency"
        if crop:
            img = trim(img)
        h, w = img.shape[:2]
        if w > widest:
            img = cv2.resize(img, (widest, round(h * widest / w)), interpolation=cv2.INTER_AREA)
        # Fully transparent pixels carry no colour worth keeping; zeroing them
        # lets WebP spend its bytes on the painting.
        img[img[..., 3] == 0, :3] = 0
        path = OUT / out
        assert cv2.imwrite(str(path), img, [cv2.IMWRITE_WEBP_QUALITY, 84]), path
        print(f"  {name:16} -> {out:18} {img.shape[1]}x{img.shape[0]}  {path.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
