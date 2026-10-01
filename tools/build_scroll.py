"""The closed handscroll in the library, drawn as a solid object, written into
index.html inside its button.

It is seen from a little to the right, so it reads as a cylinder: the near
end shows the rolled layers of paper round the wooden roller, a turned jade
knob stands out of each end, and everything on its surface (the gold lattice
of the brocade wrapper, the silk tie, the title slip) is laid onto the
curve, crowding together towards the top and bottom where the surface turns
away. Light comes from the upper left, as on the roofs.

    python tools/build_scroll.py
"""

from __future__ import annotations

import math
import re
from pathlib import Path

INDEX = Path(__file__).resolve().parent.parent / "index.html"

W, H = 640, 252
XL, XR = 104, 552          # the roll's two ends, along its axis
Y0, R = 116, 64            # axis height and radius
E = 21                     # how far a cross-section's near side bulges left (the 3/4 view)
TIE = 404                  # where the silk tie wraps round
LATTICE = 30               # lattice pitch along the axis


def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def on_surface(x: float, phi: float) -> tuple[float, float]:
    """A point on the roll at axial position x and angle phi (0 faces you,
    +90 degrees is the top), as it lands on the screen."""
    return x - E * math.cos(phi), Y0 - R * math.sin(phi)


def ring(x: float, r: float = R, e: float = E, sweep_left: bool = True) -> str:
    """The near half of the cross-section at x, top to bottom."""
    return f"M{f(x)} {f(Y0 - r)}A{f(e)} {f(r)} 0 0 {0 if sweep_left else 1} {f(x)} {f(Y0 + r)}"


def band(x0: float, x1: float) -> str:
    """A band round the roll between axial positions x0 and x1."""
    return (f"M{f(x0)} {f(Y0 - R)}H{f(x1)}A{E} {R} 0 0 0 {f(x1)} {f(Y0 + R)}"
            f"H{f(x0)}A{E} {R} 0 0 1 {f(x0)} {f(Y0 - R)}Z")


def body() -> str:
    return (f"M{XL} {Y0 - R}H{XR}A{E} {R} 0 0 1 {XR} {Y0 + R}H{XL}A{E} {R} 0 0 1 {XL} {Y0 - R}Z")


def lattice() -> tuple[str, str]:
    """Diagonal lines on the surface (x = c +/- arc length), and a gold dot
    where they cross, squashed as the surface turns away."""
    steps = [math.radians(a) for a in range(-90, 91, 6)]
    lines = []
    span = math.pi / 2 * R
    c = XL - span
    while c < XR + span:
        for sign in (1, -1):
            pts = [on_surface(c + sign * R * p, p) for p in steps]
            lines.append("M" + " ".join(f"{f(x)} {f(y)}" for x, y in pts))
        c += LATTICE
    dots = []
    c1 = XL - span
    while c1 < XR + span:
        c2 = c1
        while c2 < XR + span:
            phi = (c2 - c1) / (2 * R)
            if abs(phi) < math.radians(84):
                x, y = on_surface((c1 + c2) / 2, phi)
                ry = 2.3 * math.cos(phi)
                dots.append(f"M{f(x - 2.3)} {f(y)}a2.3 {f(ry)} 0 1 0 4.6 0a2.3 {f(ry)} 0 1 0 -4.6 0Z")
            c2 += LATTICE
        c1 += LATTICE
    return "".join(lines), "".join(dots)


def title_slip() -> tuple[str, float, float]:
    """A cream title slip pasted on the wrapper, bent round the roll."""
    x0, x1, a = 150, 290, math.radians(21)
    tl, tr = on_surface(x0, a), on_surface(x1, a)
    br, bl = on_surface(x1, -a), on_surface(x0, -a)
    path = (f"M{f(tl[0])} {f(tl[1])}L{f(tr[0])} {f(tr[1])}A{E} {R} 0 0 0 {f(br[0])} {f(br[1])}"
            f"L{f(bl[0])} {f(bl[1])}A{E} {R} 0 0 1 {f(tl[0])} {f(tl[1])}Z")
    cx, cy = on_surface((x0 + x1) / 2, 0)
    return path, cx, cy


def knob(x_root: float, direction: int, gid: str) -> str:
    """A turned jade knob on the roller, standing out of one end: a gold
    collar, a neck, a bulb and a rounded cap. Segments are drawn far end
    first on the left (its faces turn away from you) and near end first on
    the right (its faces turn towards you)."""
    profile = [(0, 15, "collar"), (5, 9, "jade"), (12, 15, "jade"), (28, 11, "jade"), (34, 0, "cap")]
    segs = []
    for (a0, r0, kind), (a1, _, _) in zip(profile, profile[1:]):
        if kind == "cap" or r0 == 0:
            continue
        x0, x1 = x_root + direction * a0, x_root + direction * a1
        lo, hi = min(x0, x1), max(x0, x1)
        e = E * r0 / R
        fill = "url(#sc-gold)" if kind == "collar" else f"url(#{gid})"
        path = (f"M{f(lo)} {f(Y0 - r0)}H{f(hi)}A{f(e)} {r0} 0 0 0 {f(hi)} {f(Y0 + r0)}"
                f"H{f(lo)}A{f(e)} {r0} 0 0 1 {f(lo)} {f(Y0 - r0)}Z")
        face = ""
        if direction > 0:   # the face at the far end of each segment turns towards you
            face = f'<ellipse cx="{f(hi)}" cy="{Y0}" rx="{f(e)}" ry="{r0}" fill="{fill}" stroke="#0b2b24" stroke-width=".6"/>'
        segs.append(f'<path d="{path}" fill="{fill}"/>{face}')
    cap_x = x_root + direction * 34
    e = E * 11 / R
    cap = (f'<ellipse cx="{f(cap_x)}" cy="{Y0}" rx="{f(e + 3)}" ry="11" fill="url(#{gid})"/>'
           f'<ellipse cx="{f(cap_x - 1)}" cy="{Y0 - 4}" rx="2" ry="3.2" fill="#e8fff6" opacity=".7"/>')
    if direction > 0:
        return "".join(segs) + cap
    return cap + "".join(reversed(segs))


def end_face() -> str:
    """The near end: the wrapper, the silk mount and the rolled paper round
    the wooden roller, ring by ring."""
    rings = [
        (1.0, "#8f1d15"),            # brocade wrapper
        (0.93, "#c9a24a"),           # its gold edge
        (0.9, "#1f3f7a"),            # blue silk mount
        (0.84, "#efe2c2"),           # the paper, rolled
    ]
    out = []
    for t, colour in rings:
        out.append(f'<ellipse cx="{XR}" cy="{Y0}" rx="{f(E * t)}" ry="{f(R * t)}" fill="{colour}"/>')
    t = 0.8
    while t > 0.26:
        out.append(f'<ellipse cx="{XR}" cy="{Y0}" rx="{f(E * t)}" ry="{f(R * t)}" fill="none" stroke="#b49a6c" stroke-width=".7" opacity=".8"/>')
        t -= 0.045
    out.append(f'<ellipse cx="{XR}" cy="{Y0}" rx="{f(E * 0.24)}" ry="{f(R * 0.24)}" fill="url(#sc-wood)"/>')
    out.append(f'<ellipse cx="{XR}" cy="{Y0}" rx="{f(E)}" ry="{R}" fill="url(#sc-face)"/>')
    return "".join(out)


def svg() -> str:
    lines, dots = lattice()
    slip, sx, sy = title_slip()
    tie_front = on_surface(TIE + 8, 0)
    return f'''<svg class="scroll-art" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false">
        <!-- Made by tools/build_scroll.py: edit that, not this. -->
        <defs>
          <clipPath id="sc-body"><path d="{body()}"/></clipPath>
          <linearGradient id="sc-round" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".13" stop-color="#000" stop-opacity=".12"/>
            <stop offset=".27" stop-color="#fff" stop-opacity=".26"/><stop offset=".38" stop-color="#fff" stop-opacity=".06"/>
            <stop offset=".68" stop-color="#000" stop-opacity=".05"/><stop offset=".88" stop-color="#000" stop-opacity=".36"/>
            <stop offset="1" stop-color="#000" stop-opacity=".62"/>
          </linearGradient>
          <linearGradient id="sc-depth" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stop-color="#000" stop-opacity=".28"/><stop offset=".35" stop-color="#000" stop-opacity="0"/>
            <stop offset=".85" stop-color="#fff" stop-opacity=".05"/><stop offset="1" stop-color="#000" stop-opacity=".12"/>
          </linearGradient>
          <linearGradient id="sc-brocade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#a8281e"/><stop offset=".5" stop-color="#9a2219"/><stop offset="1" stop-color="#6e100b"/>
          </linearGradient>
          <linearGradient id="sc-gold" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#6b4a14"/><stop offset=".25" stop-color="#f6dd96"/><stop offset=".45" stop-color="#d4a94e"/>
            <stop offset=".8" stop-color="#8a6420"/><stop offset="1" stop-color="#4f3610"/>
          </linearGradient>
          <linearGradient id="sc-jade-l" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#0d3a31"/><stop offset=".26" stop-color="#9be3cd"/><stop offset=".42" stop-color="#3fa58b"/>
            <stop offset=".8" stop-color="#17604f"/><stop offset="1" stop-color="#082620"/>
          </linearGradient>
          <linearGradient id="sc-jade-r" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#0d3a31"/><stop offset=".26" stop-color="#a9ecd7"/><stop offset=".42" stop-color="#46ae93"/>
            <stop offset=".8" stop-color="#1a6756"/><stop offset="1" stop-color="#082620"/>
          </linearGradient>
          <radialGradient id="sc-wood" cx=".4" cy=".35" r=".7">
            <stop offset="0" stop-color="#c58a4a"/><stop offset=".6" stop-color="#7a4318"/><stop offset="1" stop-color="#3a1b08"/>
          </radialGradient>
          <radialGradient id="sc-face" cx=".25" cy=".3" r=".9">
            <stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".6" stop-color="#000" stop-opacity="0"/>
            <stop offset="1" stop-color="#000" stop-opacity=".28"/>
          </radialGradient>
          <linearGradient id="sc-silk" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stop-color="#e6c26a"/><stop offset=".5" stop-color="#c99a3c"/><stop offset="1" stop-color="#8a6420"/>
          </linearGradient>
        </defs>
        <!-- The far knob, behind the roll -->
        {knob(XL - E + 6, -1, "sc-jade-l")}
        <!-- The roll: brocade, lattice, its gold edges, the title slip and the tie -->
        <path d="{body()}" fill="url(#sc-brocade)"/>
        <g clip-path="url(#sc-body)">
          <path d="{lines}" fill="none" stroke="#d9b45e" stroke-width="1.3" opacity=".8"/>
          <path d="{dots}" fill="#f2d98f"/>
          <path d="{band(XL, XL + 9)}{band(XR - 9, XR)}" fill="url(#sc-gold)"/>
          <path d="{slip}" fill="#f1e5c6" stroke="#7d1a13" stroke-width="1.4"/>
          <text x="{f(sx)}" y="{f(sy + 9)}" text-anchor="middle" font-size="27" fill="#2a1a10" style="font-family:var(--font-brush)">履 历</text>
          <rect x="{f(sx + 46)}" y="{f(sy - 7)}" width="11" height="13" fill="#b02a1e"/>
          <path d="{band(TIE, TIE + 16)}" fill="url(#sc-silk)"/>
          <path d="{ring(TIE + 4)} {ring(TIE + 12)}" fill="none" stroke="#8a6420" stroke-width=".8" opacity=".7"/>
          <rect x="0" y="{Y0 - R}" width="{W}" height="{2 * R}" fill="url(#sc-round)"/>
          <rect x="0" y="{Y0 - R}" width="{W}" height="{2 * R}" fill="url(#sc-depth)"/>
        </g>
        <!-- The near end, and its knob -->
        {end_face()}
        {knob(XR, 1, "sc-jade-r")}
        <!-- The tie's jade toggle, and its loose end with a tassel -->
        <path d="M{f(tie_front[0] - 3)} {f(tie_front[1] + 8)}C{f(tie_front[0] - 10)} {Y0 + R + 8} {f(tie_front[0] + 14)} {Y0 + R + 22} {f(tie_front[0] + 4)} {Y0 + R + 44}" fill="none" stroke="url(#sc-silk)" stroke-width="7" stroke-linecap="round"/>
        <path d="M{f(tie_front[0] + 4)} {Y0 + R + 44}l-5 18h10z" fill="#a8281e"/>
        <rect x="{f(tie_front[0] - 7)}" y="{Y0 - 16}" width="14" height="32" fill="url(#sc-jade-r)" stroke="#0b2b24" stroke-width=".8"/>
      </svg>'''


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    pattern = r'(<button class="scroll-case"[^>]*>)(.*?)(\s*</button>)'
    html, n = re.subn(pattern, lambda m: m.group(1) + "\n      " + svg() + m.group(3), html, count=1, flags=re.S)
    assert n == 1, "scroll-case button not found"
    INDEX.write_text(html, encoding="utf-8")
    print(f"scroll written ({len(svg()) // 1024} KB)")


if __name__ == "__main__":
    main()
