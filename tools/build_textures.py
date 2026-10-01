"""Weathering: two seamless textures that make the palace look painted and
old rather than printed. Both are transparent, with darker grime and lighter
sun-faded patches drawn into them, so they are simply laid over a surface;
no blend modes needed.

  wear.webp     for painted work: the beam and brackets, plaques, doors,
                marble. Soft mottling, faded patches, grain, chips, scratches.
  lacquer.webp  for the pillars: fine vertical grain, and the short
                horizontal crackle old lacquer breaks into.

    python tools/build_textures.py

Needs numpy and opencv-python. Writes into assets/gen/.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

OUT = Path(__file__).resolve().parent.parent / "assets" / "gen"
DARK = np.array((34, 18, 10), np.float32)       # umber grime
LIGHT = np.array((255, 238, 204), np.float32)   # sun-bleached paint


def periodic_noise(h: int, w: int, beta: float, rng, stretch: float = 1.0) -> np.ndarray:
    """Fractal noise that tiles seamlessly (it is made in frequency space),
    scaled to zero mean and unit spread. stretch > 1 makes it vary slowly
    up and down and quickly across: vertical streaks."""
    fy = np.fft.fftfreq(h)[:, None] * stretch
    fx = np.fft.fftfreq(w)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1
    spectrum = (rng.normal(size=(h, w)) + 1j * rng.normal(size=(h, w))) / f ** beta
    spectrum[0, 0] = 0
    n = np.real(np.fft.ifft2(spectrum))
    return (n - n.mean()) / (n.std() + 1e-9)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


class Layer:
    """A premultiplied RGBA canvas that things are composited onto."""

    def __init__(self, h: int, w: int):
        self.h, self.w = h, w
        self.rgb = np.zeros((h, w, 3), np.float32)
        self.a = np.zeros((h, w), np.float32)

    def over(self, colour: np.ndarray, alpha: np.ndarray) -> None:
        alpha = np.clip(alpha, 0, 1)
        self.rgb = colour * alpha[..., None] + self.rgb * (1 - alpha[..., None])
        self.a = alpha + self.a * (1 - alpha)

    def marks(self, colour, draw) -> None:
        """Draw with OpenCV onto a mask (wrapping at the edges, so the tile
        stays seamless), then composite the mask in `colour`."""
        mask = np.zeros((self.h * 3, self.w * 3), np.float32)
        draw(mask, self.w, self.h)
        m = np.zeros((self.h, self.w), np.float32)
        for dy in range(3):
            for dx in range(3):
                m = np.maximum(m, mask[dy * self.h:(dy + 1) * self.h, dx * self.w:(dx + 1) * self.w])
        self.over(colour, m)

    def save(self, path: Path, quality: int = 80) -> None:
        a = np.clip(self.a, 1e-4, 1)
        rgb = np.where(self.a[..., None] > 1e-4, self.rgb / a[..., None], 0)
        out = np.dstack([rgb[..., ::-1], self.a * 255]).clip(0, 255).astype(np.uint8)
        assert cv2.imwrite(str(path), out, [cv2.IMWRITE_WEBP_QUALITY, quality]), path
        print(f"  {path.name:14} {self.w}x{self.h}  {path.stat().st_size // 1024} KB")


def wear(size: int = 384, seed: int = 11) -> Layer:
    rng = np.random.default_rng(seed)
    L = Layer(size, size)
    mott = periodic_noise(size, size, 1.7, rng)
    L.over(DARK, 0.11 * smoothstep(0.2, 1.8, mott))                       # grime, settled in patches
    fade = periodic_noise(size, size, 2.0, rng)
    L.over(LIGHT, 0.09 * smoothstep(0.6, 2.0, fade))                      # paint faded by the sun
    grain = periodic_noise(size, size, 0.4, rng)
    L.over(DARK, 0.05 * smoothstep(0.3, 2.2, grain))                      # the brush's grain
    L.over(LIGHT, 0.03 * smoothstep(0.6, 2.4, -grain))

    def chips(m, w, h):
        for _ in range(110):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            r = rng.uniform(0.5, 1.5)
            cv2.ellipse(m, (int(w + x), int(h + y)), (max(1, int(r * rng.uniform(1, 2.2))), max(1, int(r))),
                        rng.uniform(0, 180), 0, 360, rng.uniform(0.18, 0.4), -1, cv2.LINE_AA)
    L.marks(DARK, chips)

    def scratches(m, w, h):
        for _ in range(14):
            x, y = rng.uniform(0, w), rng.uniform(0, h)
            a, n = rng.uniform(0, np.pi), rng.uniform(8, 34)
            p1 = (int(w + x), int(h + y))
            p2 = (int(w + x + n * np.cos(a)), int(h + y + n * np.sin(a)))
            cv2.line(m, p1, p2, rng.uniform(0.1, 0.2), 1, cv2.LINE_AA)
    L.marks(LIGHT, scratches)
    return L


def lacquer(w: int = 192, h: int = 576, seed: int = 4) -> Layer:
    rng = np.random.default_rng(seed)
    L = Layer(h, w)
    streaks = periodic_noise(h, w, 1.1, rng, stretch=9)
    L.over(DARK, 0.09 * smoothstep(0.2, 2.0, streaks))                    # grain of the lacquer
    L.over(LIGHT, 0.05 * smoothstep(0.7, 2.4, -streaks))
    mott = periodic_noise(h, w, 1.8, rng)
    L.over(DARK, 0.08 * smoothstep(0.4, 2.0, mott))
    fade = periodic_noise(h, w, 2.0, rng)
    L.over(LIGHT, 0.07 * smoothstep(0.8, 2.2, fade))
    # Crackle comes in patches, where the lacquer has dried hardest.
    patch = periodic_noise(h, w, 2.2, rng)

    def crackle(m, w_, h_):
        n = 0
        while n < 70:
            x, y = rng.uniform(0, w_), rng.uniform(0, h_)
            if patch[int(y) % h, int(x) % w] < 0.2 and rng.random() < 0.85:
                continue
            n += 1
            length = rng.uniform(5, 18)
            a = rng.normal(0, 0.12)
            pts = []
            for t in np.linspace(0, 1, 5):
                pts.append((w_ + x + t * length * np.cos(a), h_ + y + t * length * np.sin(a) + rng.normal(0, 0.5)))
            cv2.polylines(m, [np.array(pts, np.int32)], False, rng.uniform(0.18, 0.32), 1, cv2.LINE_AA)
    L.marks(DARK, crackle)

    def chips(m, w_, h_):
        for _ in range(40):
            x, y = rng.uniform(0, w_), rng.uniform(0, h_)
            cv2.circle(m, (int(w_ + x), int(h_ + y)), 1, rng.uniform(0.2, 0.4), -1, cv2.LINE_AA)
    L.marks(DARK, chips)
    return L


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    wear().save(OUT / "wear.webp")
    lacquer().save(OUT / "lacquer.webp")


if __name__ == "__main__":
    main()
