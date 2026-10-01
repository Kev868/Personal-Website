"""Stand-in artwork for the palace, generated so it can be regenerated.

Everything here is a placeholder with a known job: painted layers from the
ChatGPT image generator replace the clouds later (see docs/ASSET-BRIEF.md).
The medallion and the ornamental cloud are vector and may well stay.

    python tools/generate_assets.py

Needs numpy and opencv-python. Writes into assets/gen/.
"""

from __future__ import annotations

import math
from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "assets" / "gen"

# The palette, as in css/palace.css.
PAPER = (240, 230, 204)
CREAM = (255, 250, 240)
SHADE = (222, 212, 196)
GOLD = (201, 162, 74)
LACQUER = "#1a110d"
VERMILION = "#b8261e"
JADE = "#2e8b7a"
LAPIS = "#1f3f7a"
GOLD_HEX = "#c9a24a"
GOLD_HI = "#ecd28a"


# 1. Clouds -------------------------------------------------------------------

def value_noise(h: int, w: int, rng: np.random.Generator, base: float,
                octaves: int = 6) -> np.ndarray:
    """Fractal value noise in [0, 1]: random grids, smoothly upscaled, summed."""
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        freq = base * (2 ** o)
        grid = rng.random((int(h * freq) + 3, int(w * freq) + 3)).astype(np.float32)
        out += cv2.resize(grid, (w, h), interpolation=cv2.INTER_CUBIC) * amp
        total += amp
        amp *= 0.5
    out /= total
    return (out - out.min()) / (out.max() - out.min() + 1e-6)


def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def blobs(h: int, w: int, rng: np.random.Generator, n: int,
          ys: tuple[float, float], rs: tuple[float, float],
          xs: tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
    """A lumpy mass: the sum of soft round puffs, the way cumulus stacks."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    mass = np.zeros((h, w), np.float32)
    for _ in range(n):
        cx = rng.uniform(*xs) * w
        cy = rng.uniform(*ys) * h
        r = rng.uniform(*rs) * min(h, w)
        mass += np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
    return mass


LIT = np.array(CREAM, np.float32)
BELLY = np.array((214, 204, 196), np.float32)   # a warm lilac grey, not dead grey
RIM = np.array((236, 206, 140), np.float32)     # sunlit edge


def puff(canvas: np.ndarray, cx: float, cy: float, r: float, opacity: float,
         rng: np.random.Generator) -> None:
    """Composite one billow onto an RGBA float canvas, back to front.

    Each puff is lit from above and shaded underneath, with a ragged edge.
    Stacking many of them, lower ones last, is what makes a mass read as
    cumulus: every puff's bright crown overlaps the shaded belly behind it.
    """
    h, w = canvas.shape[:2]
    pad = int(r * 1.3) + 4
    x0, x1 = max(0, int(cx - pad)), min(w, int(cx + pad))
    y0, y1 = max(0, int(cy - pad)), min(h, int(cy + pad))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = xx - cx, yy - cy
    ang = np.arctan2(dy, dx)
    # A ragged edge: the radius wobbles with angle at a few frequencies.
    wob = sum(rng.uniform(0.012, 0.04) * np.sin(k * ang + rng.uniform(0, 6.3))
              for k in (2, 3, 5))
    dist = np.sqrt(dx * dx + dy * dy) / (r * (1 + wob))
    alpha = (1 - smoothstep(0.8, 1.0, dist)) * opacity

    # Light: bright crown, shaded belly. Normalised height inside the puff.
    ny = np.clip(dy / r, -1, 1)
    light = smoothstep(0.55, -0.6, ny)
    colour = BELLY + (LIT - BELLY) * light[..., None]
    rim = smoothstep(0.78, 0.97, dist) * smoothstep(0.1, -0.7, ny)
    colour = colour + (RIM - colour) * (rim * 0.55)[..., None]

    region = canvas[y0:y1, x0:x1]
    a = alpha[..., None]
    region[..., :3] = colour * a + region[..., :3] * (1 - a)
    region[..., 3:] = a + region[..., 3:] * (1 - a)


def finish(canvas: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Un-premultiply, add grain so it reads as paint, then BGRA for OpenCV.

    `puff` composites premultiplied colour over a canvas that starts black and
    transparent. Saved as-is, every soft edge would keep that black mixed in and
    show a dark outline against the sky.
    """
    h, w = canvas.shape[:2]
    grain = (value_noise(h, w, rng, base=0.03, octaves=3) - 0.5) * 9
    out = canvas.copy()
    a = np.clip(out[..., 3:], 1e-4, 1)
    out[..., :3] = np.where(out[..., 3:] > 1e-4, out[..., :3] / a, LIT)
    out[..., :3] = np.clip(out[..., :3] + grain[..., None], 0, 255)
    out[..., 3] = np.clip(out[..., 3], 0, 1) * 255
    return out[..., [2, 1, 0, 3]].astype(np.uint8)


def cloud_bank(w: int, h: int, seed: int, rows: int = 4) -> np.ndarray:
    """A horizontal bank: small far billows along the top, big near ones at
    the bottom, drawn in that order so the near ones overlap the far."""
    rng = np.random.default_rng(seed)
    canvas = np.zeros((h, w, 4), np.float32)
    for row in range(rows):
        t = row / max(rows - 1, 1)            # 0 = farthest row, 1 = nearest
        r_lo, r_hi = h * (0.16 + 0.12 * t), h * (0.26 + 0.2 * t)
        base_y = h * (0.42 + 0.42 * t)
        x = rng.uniform(-r_hi, 0)
        while x < w + r_hi:
            r = rng.uniform(r_lo, r_hi)
            cy = base_y + rng.uniform(-0.25, 0.25) * r
            puff(canvas, x, cy, r, opacity=0.9 + 0.1 * t, rng=rng)
            x += r * rng.uniform(0.9, 1.35)
    # A solid foot, so the bank sits on something rather than floating as beads.
    foot = smoothstep(0.78, 0.98, np.linspace(0, 1, h, dtype=np.float32))[:, None]
    under = canvas[..., 3:] < 1
    canvas[..., 3] = np.maximum(canvas[..., 3], foot[..., 0].repeat(w).reshape(h, w) * 0.95)
    canvas[..., :3] = np.where(under, np.maximum(canvas[..., :3], BELLY * foot[..., None]),
                               canvas[..., :3])
    return finish(canvas, rng)


def cloud_wall(w: int, h: int, seed: int) -> np.ndarray:
    """A tall mass for the travel transition: opaque over its left part so it
    hides the page completely, billowing along its right edge. The other
    side is the same image, mirrored in CSS."""
    rng = np.random.default_rng(seed)
    canvas = np.zeros((h, w, 4), np.float32)
    canvas[:, : int(w * 0.62), :3] = LIT
    canvas[:, : int(w * 0.62), 3] = 1
    y = -h * 0.05
    while y < h * 1.05:
        r = rng.uniform(h * 0.07, h * 0.13)
        edge = w * rng.uniform(0.6, 0.72)
        for k in range(3):                     # a few billows deep, inward
            puff(canvas, edge - k * r * 0.9, y + rng.uniform(-0.3, 0.3) * r,
                 r * rng.uniform(0.85, 1.15), opacity=1.0, rng=rng)
        y += r * rng.uniform(0.75, 1.05)
    return finish(canvas, rng)


def cloud_puff(w: int, h: int, seed: int) -> np.ndarray:
    """One clump of cloud for a distant tower to stand in: domed in the
    middle, tapering at both ends, its foot dissolving. Three rows, back to
    front, the front row lowest and widest so it covers the tower's base."""
    rng = np.random.default_rng(seed)
    canvas = np.zeros((h, w, 4), np.float32)
    for row in range(3):
        t = row / 2
        n = 5 + 2 * row
        span = 0.5 + 0.4 * t
        for i in range(n):
            u = (i + rng.uniform(0.3, 0.7)) / n
            dome = 1 - (2 * u - 1) ** 2          # 1 in the middle, 0 at the ends
            r = h * (0.15 + 0.07 * t) * (0.55 + 0.6 * dome) * rng.uniform(0.9, 1.1)
            cy = h * (0.46 + 0.16 * t) - dome * h * 0.1 * (1 - t)
            puff(canvas, w * (0.5 + (u - 0.5) * span), cy, r, opacity=1.0, rng=rng)
    foot = smoothstep(0.92, 0.66, np.linspace(0, 1, h, dtype=np.float32))[:, None]
    canvas[..., 3] *= foot
    canvas[..., :3] *= foot[..., None]            # still premultiplied here
    return finish(canvas, rng)


def save_webp(path: Path, rgba: np.ndarray, quality: int = 82) -> None:
    ok = cv2.imwrite(str(path), rgba, [cv2.IMWRITE_WEBP_QUALITY, quality])
    assert ok, path
    print(f"  {path.name:26} {rgba.shape[1]}x{rgba.shape[0]}  {path.stat().st_size // 1024} KB")


# 2. The ceiling medallion (zaojing) --------------------------------------------

def ring(n: int, r: float, shape: str, scale: float = 1.0, **attrs: str) -> str:
    """n copies of `shape`, drawn pointing up at radius r, rotated round."""
    extra = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return "".join(
        f'<g transform="rotate({360 * i / n:.3f}) translate(0 {-r:.2f}) scale({scale})" {extra}>{shape}</g>'
        for i in range(n)
    )


def band(r_out: float, r_in: float, fill: str) -> str:
    """A filled annulus with gold lines at both edges."""
    return (f'<circle r="{(r_out + r_in) / 2:.1f}" fill="none" stroke="{fill}" '
            f'stroke-width="{r_out - r_in:.1f}"/>'
            f'<circle r="{r_out}" fill="none" stroke="{GOLD_HEX}" stroke-width="2.5"/>'
            f'<circle r="{r_in}" fill="none" stroke="{GOLD_HEX}" stroke-width="2.5"/>')


def medallion() -> str:
    """Concentric bands, as a painted palace ceiling looks from directly below:
    bracket sets, lotus petals, a jewelled band, rays and a gilded pearl.
    Every band is filled; the real ceilings leave no bare wood."""
    petal = '<path d="M0 -26 C 12 -14, 12 8, 0 18 C -12 8, -12 -14, 0 -26 Z"/>'
    inner = '<path d="M0 -15 C 5 -8, 5 5, 0 10 C -5 5, -5 -8, 0 -15 Z"/>'
    bracket = ('<path d="M-9 -12 H9 V-4 H13 V4 H-13 V-4 H-9 Z"/>'
               '<rect x="-4" y="4" width="8" height="10"/>')
    jewel = '<rect x="-7" y="-7" width="14" height="14" transform="rotate(45)"/>'
    dot = '<circle r="3.2"/>'
    ray = '<path d="M0 -14 L4 0 L0 14 L-4 0 Z"/>'
    spiral = " ".join(
        f"{'M' if i == 0 else 'L'}{(2 + t * 7) * math.cos(t * 1.25):.2f} {(2 + t * 7) * math.sin(t * 1.25):.2f}"
        for i, t in enumerate(np.linspace(0, 10.5, 90))
    )
    parts = [
        f'<circle r="496" fill="{LACQUER}"/>',
        band(492, 414, "#163a33"),
        ring(36, 453, bracket, scale=1.75, fill=JADE, stroke=GOLD_HEX, stroke_width="1"),
        ring(36, 453, dot, scale=1.2, fill=GOLD_HI, transform_origin="0 0"),
        band(414, 346, "#5c1712"),
        ring(28, 380, petal, scale=1.3, fill=VERMILION, stroke=GOLD_HEX, stroke_width="1.4"),
        ring(28, 380, inner, scale=1.3, fill=GOLD_HI, opacity=".6"),
        band(346, 304, LAPIS),
        ring(44, 325, jewel, scale=1.2, fill=GOLD_HEX),
        ring(44, 325, dot, fill=VERMILION),
        band(304, 236, "#132c27"),
        ring(22, 270, petal, scale=1.35, fill=JADE, stroke=GOLD_HEX, stroke_width="1.2"),
        ring(22, 270, inner, scale=1.35, fill="#7fd1bf", opacity=".45"),
        band(236, 192, LACQUER),
        ring(56, 214, ray, scale=1.3, fill=GOLD_HEX, opacity=".9"),
        f'<circle r="192" fill="{VERMILION}" stroke="{GOLD_HEX}" stroke-width="3"/>',
        ring(16, 150, petal, scale=1.45, fill=GOLD_HEX, stroke=GOLD_HI, stroke_width="1"),
        f'<circle r="112" fill="url(#pearl)" stroke="{GOLD_HI}" stroke-width="2"/>',
        f'<path d="{spiral}" fill="none" stroke="{LACQUER}" stroke-width="3" '
        f'stroke-linecap="round" opacity=".55" transform="scale(1.3)"/>',
    ]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-500 -500 1000 1000">'
        '<defs><radialGradient id="pearl" cx="40%" cy="35%" r="70%">'
        f'<stop offset="0" stop-color="#fff3c9"/><stop offset=".45" stop-color="{GOLD_HI}"/>'
        f'<stop offset="1" stop-color="#9c7424"/></radialGradient></defs>'
        + "".join(parts) + "</svg>"
    )


# 3. The auspicious cloud (xiangyun) --------------------------------------------

def spiral_path(cx: float, cy: float, r0: float, turns: float, flip: int = 1) -> str:
    """An inward curl: radius shrinks as it turns, like a brush flicking in."""
    pts = []
    steps = int(60 * turns)
    for i in range(steps + 1):
        t = i / steps
        a = flip * (t * turns * 2 * math.pi) - math.pi / 2
        r = r0 * (1 - 0.82 * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)


def xiangyun() -> str:
    """Lobes drawn twice, stroke first and fill on top, so the outline is the
    union's silhouette with no seams where lobes overlap."""
    lobes = [(0, 0, 58), (-66, 18, 40), (64, 16, 42), (-24, -44, 30), (30, -42, 32)]
    tail = "M60 40 C 120 70, 190 60, 250 20 C 210 52, 150 84, 70 62 Z"
    shapes = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x, y, r in lobes)
    shapes += f'<path d="{tail}"/>'
    curls = "".join(
        f'<path d="{spiral_path(x, y, r * 0.78, 1.7, 1 if x >= 0 else -1)}"/>'
        for x, y, r in lobes
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-120 -90 380 170">'
        f'<g fill="#fffaf0" stroke="{GOLD_HEX}" stroke-width="10" stroke-linejoin="round">{shapes}</g>'
        f'<g fill="#fffaf0">{shapes}</g>'
        f'<g fill="none" stroke="{GOLD_HEX}" stroke-width="4" stroke-linecap="round">{curls}</g>'
        "</svg>"
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("clouds:")
    save_webp(OUT / "cloud-bank-1.webp", cloud_bank(2400, 520, seed=3))
    save_webp(OUT / "cloud-bank-2.webp", cloud_bank(2400, 520, seed=11, rows=5))
    save_webp(OUT / "cloud-bank-3.webp", cloud_bank(2400, 420, seed=27, rows=3))
    save_webp(OUT / "cloud-wall.webp", cloud_wall(1500, 1700, seed=5))
    save_webp(OUT / "cloud-puff.webp", cloud_puff(900, 420, seed=8))
    print("vector:")
    for name, svg in (("medallion.svg", medallion()), ("xiangyun.svg", xiangyun())):
        (OUT / name).write_text(svg, encoding="utf-8")
        print(f"  {name:26} {len(svg) // 1024} KB")


if __name__ == "__main__":
    main()
