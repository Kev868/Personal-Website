"""The palace roof, written into index.html's sprite: a hip roof as on the
halls of the Forbidden City, seen from the front.

Every roof on the page is this one symbol (viewBox 0 0 1600 240), coloured by
the glaze variables of the scene it stands in (--tile-base, --tile-dark,
--tile-light, --ridge); --night-dim darkens its paintwork after dark. Its
beam is fixed on purpose: it runs from x 60 to 1540 and ends at the bottom
edge, and css/palace.css stands the pillars under its two ends (and takes the
roof's height from the viewBox: 240 / 1600 = 15% of its width). Keep that if
you change anything here.

What makes it read as an imperial roof, from the bottom up:
  - the beam, painted in blue and green with gold: whirl-flower rosettes,
    chevrons, and a long cartouche of clouds round a flaming pearl;
  - a plate above it, and on that the bracket sets: blocks and arms in
    alternating blue and green, stepping out as they rise, a beak hanging
    from each, red panels with a gold pearl between them;
  - under the eave, in its order: the vermilion eave board, square flying
    rafter ends (green, gold), a red strip, round rafter ends painted as
    blue and white eyes, and at the corners the rafters' undersides fanning
    out, green on red;
  - an eave that runs level and lifts only towards the corners, finished
    with round tile ends and pointed drip tiles, a bell at each corner;
  - rows of barrel tiles, each lit along one side, stepped at every course,
    no two quite the same colour;
  - a concave slope: dark and steep under the ridge, bright where it
    flattens out towards the eave;
  - thick glazed ridges; on each hip, a procession of beasts led by an
    immortal riding a bird, each sitting on the slope; and at each end of the
    main ridge a carved finial curling up into a round scroll.

    python tools/build_roof.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

INDEX = Path(__file__).resolve().parent.parent / "index.html"
rng = np.random.default_rng(7)

H = 240
BAND_X0, BAND_X1 = 60, 1540                 # fixed: the pillars stand under the beam's ends
PILLAR = 55.2                               # a pillar's width: 3.45% of the roof's (--pillar-w in css)
DG_TOP, PLATE_TOP, BEAM_TOP = 176, 206, 212 # bracket sets; the plate under them; the beam

# The paintwork's colours (the glaze is the scene's; these are not).
RED, RED_DEEP = "#b8281c", "#6e160f"
GREEN, GREEN_HI = "#2a8a6c", "#6fcfab"
BLUE, BLUE_HI, BLUE_DEEP = "#1f4a9a", "#6a9ee6", "#0d2257"
WHITE = "#eef3ea"
TIP_L, TIP_R = 14, 1586                     # eave corners
FLAT = 330                                  # the eave is level this far either side of centre
EAVE_Y, LIFT = 152, 30                      # level eave height; how far the corners lift
RIDGE_X0, RIDGE_X1, RIDGE_TOP, RIDGE_BOT = 352, 1248, 25, 44
ROWS, COURSES = 86, 10

HIP_L = "M352 42C318 80 200 113 62 119.5Q34 118.8 16 110"
HIP_R = "M1248 42C1282 80 1400 113 1538 119.5Q1566 118.8 1584 110"


def eave(x):
    """Height of the eave's lower edge: level, then lifting to the corners."""
    d = np.clip((np.abs(np.asarray(x, float) - 800) - FLAT) / (800 - TIP_L - FLAT), 0, 1)
    return EAVE_Y - LIFT * d ** 2.2


def lift(x):
    """How far into the corner's lift x is: 0 where the eave is level, 1 at the tip."""
    return np.clip((np.abs(np.asarray(x, float) - 800) - FLAT) / (800 - TIP_L - FLAT), 0, 1)


def f(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def dots(points) -> str:
    """Many small round (or square) marks as one path: each a zero-length
    line, made a disc by a round line cap (or a square by a square one), its
    size the stroke's width. A fraction of the text of drawing circles."""
    return "".join(f"M{f(x)} {f(y)}h0" for x, y in points)


def circ(x: float, y: float, r: float) -> str:
    return f"M{f(x - r)} {f(y)}a{f(r)} {f(r)} 0 1 0 {f(2 * r)} 0a{f(r)} {f(r)} 0 1 0 {f(-2 * r)} 0Z"


def hip_points(n: int = 200) -> np.ndarray:
    """The left hip ridge's line, sampled from the main ridge to the corner."""
    t = np.linspace(0, 1, n)[:, None]
    p = np.array([[352, 42], [318, 80], [200, 113], [62, 119.5]], float)
    cubic = ((1 - t) ** 3) * p[0] + 3 * ((1 - t) ** 2) * t * p[1] + 3 * (1 - t) * t * t * p[2] + t ** 3 * p[3]
    q = np.array([[62, 119.5], [34, 118.8], [16, 110]], float)
    quad = ((1 - t) ** 2) * q[0] + 2 * (1 - t) * t * q[1] + t * t * q[2]
    return np.vstack([cubic, quad[1:]])


_hip = hip_points()


def hip_y(x: float) -> float:
    """Where the left hip ridge's line is at x (it runs right to left)."""
    return float(np.interp(x, _hip[::-1, 0], _hip[::-1, 1]))


# The roof's face, between the ridges and the eave -----------------------------

def face() -> str:
    xs = np.arange(TIP_L, TIP_R + 0.1, 8.0)
    edge = " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs, eave(xs) - 4))
    return (f"{HIP_L}L{TIP_L} {f(eave(TIP_L) - 4)}L{edge}L1584 110"
            f"Q1566 118.8 1538 119.5C1400 113 1282 80 1248 42Z")


def barrels() -> tuple[str, str, str, list[tuple[float, float, float]]]:
    """Each row of barrel tiles as three strips: its body, the edge that
    catches the light, and the side turned away from it. The channel of pan
    tiles between rows is the face's own darker fill."""
    pitch = (TIP_R - TIP_L) / ROWS
    b = pitch * 0.6
    body, light, shade, rows = [], [], [], []
    for i in range(ROWS):
        xc = TIP_L + (i + 0.5) * pitch
        foot = float(eave(xc)) - 4
        rows.append((xc, b, foot))
        for out, x0, w in ((body, xc - b / 2, b), (light, xc - b * 0.36, b * 0.22), (shade, xc + b * 0.16, b * 0.34)):
            out.append(f"M{f(x0)} 38h{f(w)}V{f(foot)}h{f(-w)}Z")
    return "".join(body), "".join(light), "".join(shade), rows


def course_y(foot: float, k: int) -> float:
    """Where course k crosses a row whose foot is at `foot`. The steep upper
    slope faces you and its courses look tall; the flatter slope near the
    eave is seen at a glance, and they crowd together."""
    t = 1 - (1 - k / COURSES) ** 1.35
    return RIDGE_BOT + (foot - RIDGE_BOT) * t


def joints(rows) -> str:
    """Each course as one line across the roof: over every barrel it dips in
    an arc (the rounded lower end of the tile above), between them it runs
    straight across the pan tiles. Used twice: once dark and a little lower,
    as the shadow under each tile's lip, once light, as the lip itself."""
    out = []
    for k in range(1, COURSES):
        x, b, foot = rows[0]
        y = course_y(foot, k)
        d = [f"M{f(x - b / 2)} {f(y)}"]
        px, py = x - b / 2, y
        for x, b, foot in rows:
            y = course_y(foot, k)
            d.append(f"l{f(x - b / 2 - px)} {f(y - py)}q{f(b / 2)} 2.2 {f(b)} 0")
            px, py = x + b / 2, y
        out.append("".join(d))
    return "".join(out)


def weathering(rows) -> tuple[str, str]:
    """Some tiles a little darker or brighter than the rest, as glaze is."""
    dark, lit = [], []
    for x, b, foot in rows:
        for k in range(COURSES):
            r = rng.random()
            if r > 0.24:
                continue
            y0, y1 = course_y(foot, k) + 1.5, course_y(foot, k + 1)
            (dark if r < 0.13 else lit).append(f"M{f(x - b / 2)} {f(y0)}h{f(b)}V{f(y1)}h{f(-b)}Z")
    return "".join(dark), "".join(lit)


# The eave ---------------------------------------------------------------------

def eave_ends(rows) -> tuple[str, str, str]:
    """A round tile end on every row and a pointed drip tile between each pair."""
    drips = []
    ends = dots((x, foot - 0.5) for x, b, foot in rows)
    for (x, b, foot), nxt in zip(rows, rows[1:] + [None]):
        if nxt:
            xm = (x + nxt[0]) / 2
            ym = float(eave(xm)) - 3
            drips.append(f"M{f(xm - 5.4)} {f(ym)}q.8 5.4 5.4 7.6q4.6-2.2 5.4-7.6Z")
    return ends, rows[0][1] * 1.04, "".join(drips)


def eave_xs(x0: float = TIP_L, x1: float = TIP_R, step: float = 6.0) -> np.ndarray:
    """Points along the eave for drawing bands that follow it: close together
    where it lifts, and only its two ends where it runs level."""
    lo = np.arange(x0, 800 - FLAT, step)
    hi = np.arange(800 + FLAT, x1, step)[1:]
    return np.concatenate([lo, [800 - FLAT, 800 + FLAT], hi, [x1]])


def strip(y0: float, y1: float) -> str:
    """A band following the eave, from y0 to y1 below its edge."""
    xs = eave_xs()
    e = eave(xs)
    return ("M" + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs, e + y0)) + "L"
            + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs[::-1], (e + y1)[::-1])) + "Z")


def deep_underside() -> str:
    """Where the eave has lifted away from the bracket sets, the underside
    shows between them: from below the round rafter ends down to the band."""
    xs = eave_xs(BAND_X0, BAND_X1, 4.0)
    top = np.minimum(eave(xs) + 23.5, DG_TOP)
    return ("M" + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs, top))
            + f"L{BAND_X1} {DG_TOP + 0.5}L{BAND_X0} {DG_TOP + 0.5}Z")


def rafter_positions():
    squares = np.arange(TIP_L + 10, TIP_R - 8, 12.6)
    return squares, squares[:-1] + 6.3


def under_eave() -> str:
    """Everything between the eave's edge and the band, in its order."""
    squares, rounds = rafter_positions()
    sq = dots((x, float(eave(x)) + 8.6) for x in squares)
    rd = dots((x, float(eave(x)) + 19.2) for x in rounds)
    fans, fan_lines = [], []
    for x in rounds:
        y = float(eave(x)) + 19.2
        top, bottom = y + 4.2, DG_TOP + 0.5
        if BAND_X0 < x < BAND_X1 and bottom - top > 1:
            # The rafters fan out round the corner: their far ends lean
            # towards the middle of the building.
            dx = (1 if x < 800 else -1) * 0.9 * float(lift(x)) ** 1.3 * (bottom - top)
            fans.append(f"M{f(x - 2.4)} {f(top)}h4.8L{f(x + 1.7 + dx)} {f(bottom)}h-3.4Z")
            fan_lines.append(f"M{f(x)} {f(top)}L{f(x + dx)} {f(bottom)}")
    deep = deep_underside()
    return f'''<!-- Under the eave: where it has lifted at the corners, the rafters fan out -->
    <path d="{deep}" fill="{RED_DEEP}"/>
    <g clip-path="url(#roof-under)">
      <path d="{''.join(fans)}" fill="{GREEN}"/>
      <path d="{''.join(fan_lines)}" fill="none" stroke="{GREEN_HI}" stroke-width=".7" opacity=".55"/>
    </g>
    <path d="{deep}" fill="url(#fan-shade)"/>
    <!-- Round eave rafters, painted as blue and white eyes, in the shadow -->
    <path d="{strip(14.4, 25)}" style="fill:var(--soffit, #24120c)"/>
    <g fill="none" stroke-linecap="round">
      <path d="{rd}" style="stroke:var(--gold)" stroke-width="9.4"/>
      <path d="{rd}" stroke="{BLUE}" stroke-width="8.8"/>
      <path d="{rd}" stroke="{WHITE}" stroke-width="6.9"/>
      <path d="{rd}" stroke="{BLUE}" stroke-width="4.7"/>
      <path d="{rd}" stroke="{BLUE_DEEP}" stroke-width="3"/>
    </g>
    <path d="{strip(12, 14.6)}" fill="{RED}"/>
    <!-- Square flying rafters, green and gold, against red -->
    <path d="{strip(5, 12.2)}" fill="{RED_DEEP}"/>
    <g fill="none" stroke-linecap="square">
      <path d="{sq}" style="stroke:var(--gold)" stroke-width="7.4"/>
      <path d="{sq}" stroke="{GREEN}" stroke-width="6.6"/>
      <path d="{sq}" style="stroke:var(--gold)" stroke-width="4.4"/>
      <path d="{sq}" stroke="{GREEN}" stroke-width="3"/>
      <path d="{sq}" style="stroke:var(--gold-hi)" stroke-width="1.5" stroke-linecap="round"/>
    </g>
    <!-- The vermilion eave board -->
    <path d="{strip(-1.5, 5)}" fill="{RED}"/>
    <path d="{strip(4.3, 5.2)}" style="fill:var(--gold)" opacity=".8"/>'''


def corner_details() -> str:
    """At each corner: a beast's head capping the corner rafter, and a bronze
    bell hanging from it."""
    out = []
    for flip in (False, True):
        g = 'transform="translate(1600 0) scale(-1 1)"' if flip else ""
        out.append(f'''<g {g}>
      <path d="M8 124c-3 1.5-3.5 6-1 8.5 2.5 2 7 1.5 9.5-1l2-5c-3-3-7-3.5-10.5-2.5Z" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width=".9"/>
      <path d="M22 147v6" style="stroke:var(--gold-deep)" stroke-width="1"/>
      <path d="M18.5 160q0-7 3.5-7q3.5 0 3.5 7Z" style="fill:var(--gold-deep);stroke:#3a2608" stroke-width=".6"/>
      <path d="M21.4 160v2.6" style="stroke:var(--gold-deep)" stroke-width="1.2"/>
    </g>''')
    return "".join(out)


# The band: bracket sets, the plate and the beam ------------------------------------

def bracket_sets() -> str:
    """Twenty bracket sets, one per 74 units of band. Each is a block on the
    plate, an arm on that with blocks at its ends, a longer arm above with
    blocks of its own, and a beak hanging in front; blue and green change
    places from one set to the next. Red panels between, each with a pearl."""
    def arm(cx, h, y0, y1):
        return (f"M{f(cx - h)} {y0}H{f(cx + h)}V{f(y1 - 2.6)}Q{f(cx + h)} {y1} {f(cx + h - 3)} {y1}"
                f"H{f(cx - h + 3)}Q{f(cx - h)} {y1} {f(cx - h)} {f(y1 - 2.6)}Z")

    def block(x, y0, y1, w=3.6):
        return f"M{f(x - w)} {y0}H{f(x + w)}L{f(x + w - 1)} {y1}H{f(x - w + 1)}Z"

    # Painted by hand: no two sets quite the same blue or green.
    greens = [GREEN, "#2f9273", "#26805f", "#32906c"]
    blues = [BLUE, "#244f9e", "#1b438d", "#2753a4"]
    parts, beaks, lights = {}, {}, []
    for i in range(20):
        cx = BAND_X0 + 37 + 74 * i
        g, bl = greens[int(rng.integers(4))], blues[int(rng.integers(4))]
        a, b = (g, bl) if i % 2 == 0 else (bl, g)
        for d in (parts, beaks):
            d.setdefault(a, []); d.setdefault(b, [])
        parts[b].append(f"M{f(cx - 8.5)} 198H{f(cx + 8.5)}L{f(cx + 6.5)} 206H{f(cx - 6.5)}Z")
        parts[a].append(arm(cx, 17, 192, 198))
        parts[a].append(arm(cx, 26, 181, 187))
        for dx in (-14, 14):
            parts[b].append(block(cx + dx, 187, 192))
        for dx in (-22, 0, 22):
            parts[b].append(block(cx + dx, 176.5, 181))
        beaks[b].append(f"M{f(cx - 4.2)} 182H{f(cx + 4.2)}V199L{f(cx)} 204.5L{f(cx - 4.2)} 199Z")
        lights.append(f"M{f(cx - 15)} 193H{f(cx + 15)}M{f(cx - 24)} 182H{f(cx + 24)}")
    pearls = [BAND_X0 + 74 * i for i in range(1, 20)]
    flames = "".join(f"M{f(x - 2.6)} 196Q{f(x - 1)} 190.5 {f(x)} 188.6Q{f(x + 1)} 190.5 {f(x + 2.6)} 196" for x in pearls)
    pearl_dots = "".join(circ(x, 197.2, 2.3) for x in pearls)
    w = BAND_X1 - BAND_X0
    return f'''<rect x="{BAND_X0}" y="{DG_TOP}" width="{w}" height="{PLATE_TOP - DG_TOP}" fill="{RED_DEEP}"/>
    <path d="{flames}" style="fill:var(--gold)" opacity=".85"/>
    <path d="{pearl_dots}" style="fill:var(--gold-hi)"/>
    {"".join(f'<path d="{"".join(v)}" fill="{k}" style="stroke:var(--gold)" stroke-width=".9"/>' for k, v in parts.items() if v)}
    <path d="{''.join(lights)}" stroke="{WHITE}" stroke-width=".7" opacity=".55"/>
    {"".join(f'<path d="{"".join(v)}" fill="{k}" style="stroke:var(--gold)" stroke-width=".9"/>' for k, v in beaks.items() if v)}
    <rect x="{BAND_X0}" y="{DG_TOP}" width="{w}" height="{PLATE_TOP - DG_TOP}" fill="url(#dg-shade)"/>'''


def plate() -> str:
    """The plate the bracket sets stand on: blue, a gold cloud under each set."""
    w = BAND_X1 - BAND_X0
    clouds = "".join(f"M{f(x - 6)} 209Q{f(x)} 206.6 {f(x + 6)} 209Q{f(x)} 211.4 {f(x - 6)} 209Z"
                     for x in (BAND_X0 + 37 + 74 * i for i in range(20)))
    return f'''<rect x="{BAND_X0}" y="{PLATE_TOP}" width="{w}" height="{BEAM_TOP - PLATE_TOP}" fill="{BLUE}"/>
    <path d="{clouds}" style="fill:var(--gold)"/>'''


def beam() -> str:
    """The beam, painted end to end: a gold-striped band at each end over the
    pillar, then whirl-flower rosettes with diamonds between, a gold chevron,
    and in the middle a long cartouche of clouds round a flaming pearl."""
    w = BAND_X1 - BAND_X0
    y = (BEAM_TOP + H) / 2
    left = [140, 214, 288, 362, 436]
    diamonds = [177, 251, 325, 399, 473]
    xs_r = left + [1600 - x for x in left]
    xs_d = diamonds + [1600 - x for x in diamonds]
    disks = "".join(circ(x, y, 11) for x in xs_r)
    petals = "".join(circ(x + 7.2 * np.cos(a), y + 7.2 * np.sin(a), 3.3)
                     for x in xs_r for a in np.linspace(0, 2 * np.pi, 8, endpoint=False))
    cores = "".join(circ(x, y, 4.2) for x in xs_r)
    dots = "".join(circ(x, y, 1.5) for x in xs_r + xs_d)
    dia = "".join(f"M{f(x)} {f(y - 9.5)}L{f(x + 7.5)} {f(y)}L{f(x)} {f(y + 9.5)}L{f(x - 7.5)} {f(y)}Z" for x in xs_d)
    dia_in = "".join(f"M{f(x)} {f(y - 5.7)}L{f(x + 4.5)} {f(y)}L{f(x)} {f(y + 5.7)}L{f(x - 4.5)} {f(y)}Z" for x in xs_d)
    chevrons = "M528 213L514 226L528 239M536 213L522 226L536 239M1072 213L1086 226L1072 239M1064 213L1078 226L1064 239"
    # The band at each end is exactly a pillar's width, straight above it.
    e0, e1 = BAND_X0, BAND_X0 + PILLAR
    ends = "".join(f"M{f(x)} {BEAM_TOP}V{H}M{f(1600 - x)} {BEAM_TOP}V{H}" for x in (e0 + 4, e1 - 4))
    end_lines = "".join(f"M{f(x)} {BEAM_TOP}V{H}M{f(1600 - x)} {BEAM_TOP}V{H}" for x in (e0 + 8, e1 - 8))
    # Clouds rolling along the cartouche, curling as they go, round the pearl.
    wave = ("M580 226C600 216 624 216 640 226S684 236 704 226S744 216 764 226"
            "M836 226C856 236 880 236 896 226S940 216 960 226S1000 236 1020 226")
    curls = "".join(f"M{x} 226a5 5 0 1 1 5 5a2.6 2.6 0 1 1 -2.6 -2.6" for x in (612, 676, 740, 860, 924, 988))
    pearl = circ(800, 226, 4.4)
    return f'''<rect x="{BAND_X0}" y="{BEAM_TOP}" width="{w}" height="{H - BEAM_TOP}" fill="{GREEN}"/>
    <path d="M{e0} {BEAM_TOP}h{PILLAR}v{H - BEAM_TOP}h-{PILLAR}ZM{f(1600 - e1)} {BEAM_TOP}h{PILLAR}v{H - BEAM_TOP}h-{PILLAR}Z" fill="{BLUE}"/>
    <path d="{ends}" style="stroke:var(--gold)" stroke-width="1.4"/>
    <path d="{end_lines}" stroke="{WHITE}" stroke-width=".8"/>
    <path d="{circ(e0 + PILLAR / 2, y, 6)}{circ(1600 - e0 - PILLAR / 2, y, 6)}" fill="{GREEN}" style="stroke:var(--gold)" stroke-width="1"/>
    <path d="{circ(e0 + PILLAR / 2, y, 2)}{circ(1600 - e0 - PILLAR / 2, y, 2)}" style="fill:var(--gold-hi)"/>
    <path d="{disks}" fill="{BLUE}" stroke="{WHITE}" stroke-width=".9"/>
    <path d="{petals}" fill="{BLUE_HI}" stroke="{WHITE}" stroke-width=".5"/>
    <path d="{cores}" fill="{GREEN}" style="stroke:var(--gold)" stroke-width=".8"/>
    <path d="{dia}" fill="{BLUE}" style="stroke:var(--gold)" stroke-width="1"/>
    <path d="{dia_in}" fill="none" stroke="{WHITE}" stroke-width=".6"/>
    <path d="{chevrons}" fill="none" style="stroke:var(--gold)" stroke-width="1.3"/>
    <path d="M540 226L558 214.8H1042L1060 226L1042 237.2H558Z" fill="{BLUE}" style="stroke:var(--gold)" stroke-width="1.4"/>
    <path d="M546 226L560.5 217.4H1039.5L1054 226L1039.5 234.6H560.5Z" fill="none" stroke="{WHITE}" stroke-width=".7"/>
    <path d="{wave}{curls}" fill="none" style="stroke:var(--gold)" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M793 223Q796 214 800 211Q804 214 807 223Z" style="fill:var(--gold)"/>
    <path d="{pearl}" style="fill:var(--gold-hi);stroke:var(--gold)" stroke-width=".8"/>
    <path d="{dots}" style="fill:var(--gold-hi)"/>
    <rect x="{BAND_X0}" y="{BEAM_TOP}" width="{w}" height="{H - BEAM_TOP}" fill="url(#beam-shade)"/>
    <path d="M{BAND_X0} {BEAM_TOP + 0.7}H{BAND_X1}M{BAND_X0} {H - 0.7}H{BAND_X1}" style="stroke:var(--gold)" stroke-width="1.3"/>'''


BRACE = ("M0 0H86C82 4 76 6 70 6C66 6 64 9 66 12C58 13 52 14 48 18C44 15 38 16 34 20"
         "C30 22 28 26 30 30C22 29 14 30 8 34C4 36 1.6 36 0 35Z")
BRACE_INNER = "M6 4H62C58 7 54 9 50 9C40 10 30 14 24 20C18 24 12 26 6 28Z"
BRACE_SCROLL = "M10 24C20 14 34 10 52 6M30 13a4 4 0 1 1 4 4M14 22a3 3 0 1 1 3 3"


def braces() -> str:
    """Sparrow braces: carved, painted brackets in the angle between each
    pillar and the beam, scalloped underneath, with a gold scroll. They hang
    below the drawing's edge; a roof without pillars hides them (--braces)."""
    one = f'''<path d="{BRACE}" fill="{GREEN}" style="stroke:var(--gold)" stroke-width="1.2"/>
      <path d="{BRACE_INNER}" fill="{BLUE}" opacity=".9"/>
      <path d="{BRACE_SCROLL}" fill="none" style="stroke:var(--gold)" stroke-width="1.2" stroke-linecap="round"/>
      <path d="M2 1.2H84" stroke="{WHITE}" stroke-width=".7" opacity=".6"/>
      <path d="{BRACE}" fill="url(#wear-tex)"/>'''
    x = BAND_X0 + PILLAR
    return (f'<g style="display:var(--braces, inline)">'
            f'<g transform="translate({f(x)} {H})">{one}</g>'
            f'<g transform="translate({f(1600 - x)} {H}) scale(-1 1)">{one}</g></g>')


def weathered() -> str:
    """Everything painted under the eave: the band and the underside. (The
    braces carry their own, so it goes when they do.)"""
    xs = eave_xs()
    e = eave(xs)
    bottom = np.where((xs >= BAND_X0) & (xs <= BAND_X1), H, e + 25)
    region = ("M" + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs, e - 1.5)) + "L"
              + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs[::-1], bottom[::-1])) + "Z")
    return region


def night_veil() -> str:
    """After dark the paintwork under the roof falls into shadow: everything
    from the eave board down, as one shape, darkened by --night-dim."""
    xs = eave_xs()
    e = eave(xs)
    bottom = np.where((xs >= BAND_X0) & (xs <= BAND_X1), H, e + 25)
    d = ("M" + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs, e - 1.5)) + "L"
         + " ".join(f"{f(x)} {f(y)}" for x, y in zip(xs[::-1], bottom[::-1])) + "Z")
    return f'<path d="{d}" fill="#000" style="opacity:var(--night-dim, 0)"/>'


# The ridges --------------------------------------------------------------------

# Figures on the ridges. Each is drawn once, in the defs, and placed with <use>.
# The beasts face left and stand on their base at (0, 0), about 15 units tall;
# each is a silhouette in the glaze, shaded, with carved lines in the ridge's
# colour, a highlight where the light catches it, and an eye.

def spiral(cx: float, cy: float, r0: float, r1: float, turns: float, start: float = 0.0, cw: bool = True) -> str:
    """A spiral line from radius r0 in to r1, for carved whorls and curls."""
    t = np.linspace(0, 1, max(12, int(28 * turns)))
    a = start + (1 if cw else -1) * 2 * np.pi * turns * t
    r = r0 + (r1 - r0) * t
    return "M" + " ".join(f"{f(cx + rr * np.cos(aa))} {f(cy + rr * np.sin(aa))}" for rr, aa in zip(r, a))


LION = dict(
    body=("M-5.4 0L-5.6-1.2L-4.8-1.4L-4.6-6.8C-5.2-8-6.2-8.6-7.4-9L-8.8-9.4L-7.8-10.4L-9.4-10.8"
          "C-9.6-12.2-8.6-13.2-7.4-13.4C-7-14.6-6-15.2-5-15C-4-16.2-2.4-16-2-14.8C-.6-14.8-.4-13.2-1.2-12.4"
          "C0-11.6 0-10-1-9.4C1.6-9.4 3.6-8 4.2-5.8C5-6.6 6.6-8.6 6.4-11C7.6-9.6 7.8-6.4 5.4-4.4"
          "C5.6-2.6 5.4-1 4.4 0L1.6 0L1.2-2.2L-2.6-2.2L-3 0Z"),
    carve=("M-4.4-12.8c.8-.9 1.9-.7 2.2.3M-3.8-10.4c.8-.7 1.8-.5 2 .4M-3.2-8c.7-.6 1.6-.4 1.8.4"
           "M2.4-4.2c.4-1.4 2-1.6 2.6-.4M-4.6-3.4V-1.4M-8.6-10.6L-6.8-10.8"),
    lit="M-.8-9.6C1.2-9.4 3-8.2 3.8-6.2M-7.2-13.2C-6.6-14.2-5.8-14.6-5-14.6",
    eye=(-6.6, -12.3),
)

DRAGON = dict(
    body=("M-5.4 0L-5.6-1.2L-4.8-1.4L-4.6-6.4C-5-7.8-6-8.4-7.2-8.8L-10.2-9.4L-8.2-10.4L-10.8-11"
          "C-10.6-12-9.6-12.4-8.4-12.6L-6.6-13.2L-4.6-16.6L-4.4-14L-3.4-15.8L-3-13.2"
          "L-1.8-12.2L-.4-13L-.8-11L.9-11.3L.4-9.5L2.3-9.2C3.4-8.4 4.2-7 4.4-5.6"
          "C5.4-6.4 6.6-8 6-10C7.4-8.6 7.6-6 5.4-4.2C5.6-2.6 5.4-1 4.4 0L1.6 0L1.2-2.2L-2.6-2.2L-3 0Z"),
    carve=("M-10.6-10.6c-.9.6-1.3 1.7-.7 2.6M-3.6-6.4c.6-.6 1.4-.6 2 0M-2.8-4.4c.6-.6 1.4-.6 2 0"
           "M-.8-6.8c.6-.6 1.4-.6 2 0M2.4-4.2c.4-1.4 2-1.6 2.6-.4M-9.6-10.4L-7.6-10.2"),
    lit="M-.4-9.4C1.6-9 3.2-7.6 3.9-6M-8.6-12.4L-6.8-12.9",
    eye=(-7.2, -11.6),
)

PHOENIX = dict(
    body=("M-1.6 0L-1.4-3L-2.6-4C-3.8-5.2-4-7.2-3.4-8.6C-3.6-9.8-4.2-10.8-5-11.4L-7.6-11.6L-5.6-12.6"
          "C-5.4-13.8-4.4-14.4-3.4-14.2L-2.6-16.6L-2.2-14.4L-.9-16L-1.3-13.6C-1.6-12.4-2-11-1.4-10"
          "C.4-10.4 2.2-9.2 2.6-7.4C4-8.8 5.2-11.6 4.8-14.6C6.4-12.6 6.8-9.4 5.8-7.2"
          "C7.2-8.4 8-10.4 7.8-12.2C8.8-9.6 8.2-6.4 5.6-4.6C4.2-3.6 2.4-3.2 1-3.2L.4-3L.6 0Z"),
    carve=("M-1.6-8.4C-.2-9 1.4-8.6 2-7.4M-1.2-6.6C.2-7.2 1.4-6.8 2-5.8M4.8-13.2C4.6-10 3.8-8 2.8-6.6"
           "M6.6-9.6C6-7.6 5-6.2 3.8-5.4"),
    lit="M-2.8-8.2C-3.2-9.6-3.6-10.6-4.4-11.2M-.8-10.2C.6-10 1.8-9.2 2.3-8",
    eye=(-4.4, -12.8),
)

HORSE = dict(
    body=("M-5.2 0L-5.4-1.2L-4.6-1.4L-4.4-7C-4.6-8.6-5.4-10-6.6-10.8L-9.2-11.4C-9.8-11.6-10-12.6-9.4-13"
          "L-6.8-14L-5.6-15.8L-5-14.4L-4-14.6L-3.4-13.2L-2.4-13.4L-2.4-12L-1.2-11.8L-1.6-10.4"
          "C1-10.2 3.4-8.6 4-6C5.4-6.2 6.4-7.6 6.6-9.4C7.2-7.2 6.6-5.2 5.2-3.8"
          "C5.4-2.4 5.2-1 4.4 0L1.6 0L1.2-2.2L-2.4-2.2L-2.8 0Z"),
    carve=("M-4.6-13.4C-3.6-12.6-3-11.4-3-10M-3.4-11.8C-2.4-11-2-10-2-9M2.2-4.2c.4-1.4 2-1.6 2.6-.4"
           "M-9.2-12.2h.9M-4.4-3.4V-1.4"),
    lit="M-1.2-10.2C1.2-9.8 3-8.4 3.6-6.4M-9-12.8L-7-13.6",
    eye=(-7, -12.6),
)

IMMORTAL = dict(
    body=("M-2 0L-1.8-2C-4.4-2.2-6.4-3.4-6.8-5.4C-7-6.6-6.6-7.4-7.6-7.8L-9.4-7.6L-7.8-8.8"
          "C-7.4-9.8-6.2-9.8-5.8-8.8C-5.4-7.6-5.2-6.6-4.2-6.2L-3.4-6.2L-3.2-9.6"
          "C-3.4-10.4-3.2-11-2.8-11.4C-3.6-11.8-3.8-12.8-3.2-13.4L-4.2-13.6L-1.6-15.4L.8-13.6L-.2-13.4"
          "C.4-12.8.2-11.8-.6-11.4C-.2-11-.1-10.4-.3-9.6L.8-6.2"
          "C2.8-6.2 4.2-7.6 4.8-10C5.8-8 5.8-5.6 4.4-4C3.4-2.8 1.6-2.2.4-2.2L.2 0Z"),
    carve=("M-3-9.4C-2.2-8.8-1.2-8.8-.4-9.4M-3.2-7.6h3.6M-6.4-5.2C-5-4.6-3.4-4.6-2-5.2M1.4-4.4C2.6-4.8 3.6-5.8 4.2-7.4"),
    lit="M-6.6-6.2C-6.4-4.6-5.2-3.4-3.6-3M-2.8-13.6L-1.6-14.6",
    eye=(-1.7, -12.4),
)

# The larger beast where the procession starts: a horned dragon's head and
# neck, facing the corner, jaws open.
HIP_BEAST = dict(
    body=("M-5 0C-5.4-2-6.2-4-7.2-6L-11-6.4L-8.4-8L-11.6-9C-11.4-10.6-10-11.4-8.6-11.4C-8-12.6-7-13.4-5.6-13.4"
          "L-4-17.8L-3.2-14L-1.6-17L-1.4-13.2L.6-14.2L0-12L2.6-12.8L1.6-10.2L4.4-10.6L3-8"
          "L6.4-8.2L5.4-5.8L8-5C8.8-3.4 8.8-1.6 8.2 0Z"),
    carve=("M-10.4-6.6l.5-1.4.6 1.2M-10.6-8.8l.6 1.1.6-1M-11.2-9.8c-1-.2-1.8.6-1.6 1.6"
           "M-5-10.8C-3.2-10.6-1.8-9.6-1.2-8M-4.6-8.4C-3-8.2-1.8-7.2-1.4-6"
           "M-3.6-3c.7-.7 1.6-.7 2.2 0M-.4-3.4c.7-.7 1.6-.7 2.2 0M2.8-3.2c.7-.7 1.6-.7 2.2 0"),
    lit="M-8.4-11C-7.8-12.2-6.8-12.8-5.6-12.9M-4.2-16.6L-3.6-14.4M-4.6-1.6C-5.2-3-5.8-4.4-6.6-5.6",
    eye=(-7.4, -10.4),
)

FIGURES = {"lion": LION, "dragon": DRAGON, "phoenix": PHOENIX, "horse": HORSE,
           "immortal": IMMORTAL, "hipbeast": HIP_BEAST}


def figure_defs() -> str:
    out = []
    for name, fig in FIGURES.items():
        ex, ey = fig["eye"]
        out.append(f'''    <g id="rb-{name}">
      <path d="{fig['body']}" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width=".6" stroke-linejoin="round"/>
      <path d="{fig['body']}" fill="url(#beast-shade)"/>
      <path d="{fig['lit']}" fill="none" style="stroke:var(--tile-light)" stroke-width=".7" stroke-linecap="round"/>
      <path d="{fig['carve']}" fill="none" style="stroke:var(--ridge)" stroke-width=".45" stroke-linecap="round"/>
      <path d="{circ(ex, ey, .75)}" style="fill:var(--ridge)"/>
    </g>
''')
    out.append(finial_def())
    return "".join(out)


def procession() -> str:
    """On each hip, near the corner: the immortal on a bird at the front, then
    a dragon, a phoenix, a lion, two heavenly horses and another lion, and the
    larger horned beast where the procession starts. Each sits on the ridge
    turned to its slope there, its feet flush on the top of the ridge."""
    figures = [(36, "immortal", 1.2)]
    for x, name in zip((52, 68, 84, 100, 116, 132), ("dragon", "phoenix", "lion", "horse", "horse", "lion")):
        figures.append((x, name, 1.2))
    figures.append((166, "hipbeast", 1.4))
    out = []
    for x, name, s in figures:
        y = hip_y(x)
        m = (hip_y(x + 1.5) - hip_y(x - 1.5)) / 3            # the slope here
        a = np.degrees(np.arctan(m))
        nx, ny = m / np.hypot(1, m), -1 / np.hypot(1, m)       # straight up, off the ridge
        bx, by = x + 4.6 * nx, y + 4.6 * ny                    # a little into its top, so it sits
        out.append(f'<use href="#rb-{name}" transform="translate({f(bx)} {f(by)}) rotate({f(a)}) scale({s})"/>')
        out.append(f'<use href="#rb-{name}" transform="translate({f(1600 - bx)} {f(by)}) rotate({f(-a)}) scale({-s} {s})"/>')
    return "".join(out)


# The finial on each end of the main ridge, drawn for the right end: its
# origin is the ridge's end at its foot, and the ridge (19 units tall) runs
# off to the left, into its base. A carved base, and rising out of it a body
# that sweeps up and curls inward over the ridge into a round scroll.
# Square where it meets the main ridge; rounded on the outside, where the hip
# ridge falls away beneath it, so no corner is left standing in the air.
FINIAL_BASE = "M-8.4 0H4.4C10 0 14.4-4.6 14.4-10.6V-20.4H-8.4Z"
FINIAL_BODY = "M-6.4-20.2C-6.2-24-7-27.2-8.6-30L7.2-43C13-38.4 15-28.4 13.2-20.2Z"
SCROLL = (-1.2, -35.6, 9.4)                    # the curl, seen end on: centre and radius


def finial_def() -> str:
    cx, cy, r = SCROLL
    # Lotus petals along the top of the base, and a bead line under them.
    petals = "".join(f"M{f(x - 2.2)} -16.4Q{f(x - 2.2)} -19.6 {f(x)} -20.2Q{f(x + 2.2)} -19.6 {f(x + 2.2)} -16.4Z"
                     for x in np.arange(-6.2, 13, 4.4))
    beads = dots((x, -14.6) for x in np.arange(-6.6, 13.6, 2.2))
    # A ruyi cloud carved on the face of the base.
    cloud = ("M-2.4-6.6c-2.4 0-2.8-3.6-.4-4.2c.4-2.2 3.6-2.6 4.4-.6c1-1.8 4-1.2 4 .9"
             "c2.2.2 2.4 3.6.2 3.9Z"
             "M-.6-8.8a1.2 1.2 0 1 1 1.6 1.2M4.2-8.6a1.1 1.1 0 1 1 1.4 1.1")
    # Grooves running up the body, following its outer edge.
    grooves = "".join(f"M{f(12.6 - k * 3.2)} -21C{f(14 - k * 3.4)} -28 {f(12.4 - k * 3.6)} -35 {f(7.6 - k * 3.2)} {f(-40.4 + k * 2.2)}"
                      for k in range(1, 4))
    scales = "".join(f"M{f(x - 1.3)} {f(y)}q1.3 1.5 2.6 0" for y in (-23.6, -26.8) for x in np.arange(-4.2 + (y == -26.8) * 1.3, 11, 2.6))
    groove = spiral(cx, cy, r - 3.2, 1.2, 2.2, start=np.pi * 0.5, cw=False)
    ring_beads = dots((cx + (r - 1.6) * np.cos(t), cy + (r - 1.6) * np.sin(t))
                      for t in np.linspace(0, 2 * np.pi, 16, endpoint=False))
    return f'''    <g id="rb-finial">
      <path d="{FINIAL_BODY}" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width="1" stroke-linejoin="round"/>
      <path d="{FINIAL_BODY}" fill="url(#chiwen-shade)"/>
      <path d="{scales}" fill="none" style="stroke:var(--ridge)" stroke-width=".5" opacity=".7"/>
      <path d="{grooves}" fill="none" style="stroke:var(--ridge)" stroke-width=".7" stroke-linecap="round"/>
      <path d="M13.4-21C14.6-28.6 12.8-37.6 7.6-42.2" fill="none" style="stroke:var(--tile-light)" stroke-width=".8" opacity=".6" transform="translate(-1.6 0)"/>
      <path d="{FINIAL_BASE}" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width="1"/>
      <path d="{FINIAL_BASE}" fill="url(#chiwen-shade)"/>
      <path d="{petals}" style="fill:var(--tile-light);stroke:var(--ridge)" stroke-width=".5"/>
      <path d="{beads}" fill="none" style="stroke:var(--ridge)" stroke-width="1.3" stroke-linecap="round"/>
      <path d="M-8.4-12.6H14.4M-8.4-2.4H10.2" style="stroke:var(--ridge)" stroke-width=".7"/>
      <path d="{cloud}" fill="none" style="stroke:var(--ridge)" stroke-width=".7" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="{circ(cx, cy, r)}" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width="1.1"/>
      <path d="{circ(cx, cy, r)}" fill="url(#scroll-shade)"/>
      <path d="{ring_beads}" fill="none" style="stroke:var(--tile-light)" stroke-width="1.2" stroke-linecap="round"/>
      <path d="{circ(cx, cy, r - 2.8)}" fill="none" style="stroke:var(--ridge)" stroke-width=".7"/>
      <path d="{groove}" fill="none" style="stroke:var(--ridge)" stroke-width=".9" stroke-linecap="round"/>
      <path d="{circ(cx, cy, 1.3)}" style="fill:var(--tile-light);stroke:var(--ridge)" stroke-width=".5"/>
      <path d="M{f(cx - r * .75)} {f(cy - r * .55)}A{r} {r} 0 0 1 {f(cx + r * .45)} {f(cy - r * .9)}" fill="none" style="stroke:var(--tile-light)" stroke-width="1" stroke-linecap="round" opacity=".8"/>
    </g>
'''


def chiwen() -> str:
    return (f'<use href="#rb-finial" transform="translate({RIDGE_X1} {RIDGE_BOT})"/>'
            f'<use href="#rb-finial" transform="translate({RIDGE_X0} {RIDGE_BOT}) scale(-1 1)"/>')


def main_ridge() -> str:
    joints_ = "".join(f"M{x} 32.5v7" for x in range(RIDGE_X0 + 10, RIDGE_X1 - 4, 12))
    w = RIDGE_X1 - RIDGE_X0
    return f'''<rect x="{RIDGE_X0}" y="{RIDGE_TOP}" width="{w}" height="{RIDGE_BOT - RIDGE_TOP}" style="fill:var(--tile-base);stroke:var(--ridge)" stroke-width="1.3"/>
    <rect x="{RIDGE_X0}" y="{RIDGE_TOP}" width="{w}" height="{RIDGE_BOT - RIDGE_TOP}" fill="url(#ridge-shade)"/>
    <path d="M{RIDGE_X0} 27.2H{RIDGE_X1}" style="stroke:var(--tile-light)" stroke-width="2.2" opacity=".85"/>
    <path d="M{RIDGE_X0} 31.5H{RIDGE_X1}M{RIDGE_X0} 40.5H{RIDGE_X1}" style="stroke:var(--ridge)" stroke-width="1"/>
    <path d="{joints_}" style="stroke:var(--ridge)" stroke-width=".8" opacity=".7"/>'''


def hips() -> str:
    both = HIP_L + HIP_R
    return f'''<path d="{both}" fill="none" style="stroke:var(--ridge)" stroke-width="11.5" stroke-linecap="round"/>
    <path d="{both}" fill="none" style="stroke:var(--tile-base)" stroke-width="8.6" stroke-linecap="round"/>
    <path d="{both}" fill="none" style="stroke:var(--tile-light)" stroke-width="2" opacity=".7" transform="translate(0 -2.4)"/>'''


# Assembly ----------------------------------------------------------------------

def symbol() -> str:
    body, light, shade, rows = barrels()
    dark, lit = weathering(rows)
    ends, end_d, drips = eave_ends(rows)
    return f'''<symbol id="roof" viewBox="0 0 1600 {H}" overflow="visible">
    <!-- Made by tools/build_roof.py: edit that, not this. -->
    <!-- The band: bracket sets on a plate, over the painted beam -->
    {bracket_sets()}
    {plate()}
    {beam()}
    {braces()}
    {under_eave()}
    {corner_details()}
    <!-- Weathering over the paintwork: grime, faded patches, chips -->
    <path d="{weathered()}" fill="url(#wear-tex)"/>
    <path d="{weathered()}" fill="url(#age-light)"/>
    {night_veil()}
    <!-- The tiled face -->
    <path d="{face()}" style="fill:var(--tile-dark)"/>
    <g clip-path="url(#roof-clip)">
      <path d="{body}" style="fill:var(--tile-base)"/>
      <path d="{dark}" fill="#000" opacity=".11"/>
      <path d="{lit}" style="fill:var(--tile-light)" opacity=".22"/>
      <path d="{light}" style="fill:var(--tile-light)" opacity=".75"/>
      <path d="{shade}" fill="#000" opacity=".2"/>
      <use href="#roof-joints" fill="none" stroke="#000" stroke-width="1.5" opacity=".34" transform="translate(0 1.5)"/>
      <use href="#roof-joints" fill="none" style="stroke:var(--tile-light)" stroke-width="1" opacity=".6"/>
      <rect x="0" y="{RIDGE_BOT - 2}" width="1600" height="16" fill="url(#ridge-cast)"/>
      <path d="{HIP_L}{HIP_R}" fill="none" stroke="#000" stroke-width="6" opacity=".2" transform="translate(0 6)"/>
      <path d="{face()}" fill="url(#roof-shade-v)"/>
      <path d="{face()}" fill="url(#roof-shade-h)"/>
      <path d="{face()}" fill="url(#wear-tex)" opacity=".6"/>
    </g>
    <!-- The eave's edge: drip tiles, then round tile ends, casting a little
         shadow on the eave board -->
    <path d="{drips}" fill="#000" opacity=".3" transform="translate(0 1.6)"/>
    <path d="{ends}" fill="none" stroke="#000" stroke-width="{f(end_d)}" stroke-linecap="round" opacity=".3" transform="translate(0 1.6)"/>
    <path d="{drips}" style="fill:var(--tile-base);stroke:var(--tile-dark)" stroke-width=".7"/>
    <g fill="none" stroke-linecap="round">
      <path d="{ends}" style="stroke:var(--tile-dark)" stroke-width="{f(end_d + 1)}"/>
      <path d="{ends}" style="stroke:var(--tile-light)" stroke-width="{f(end_d - 1)}"/>
      <path d="{ends}" style="stroke:var(--tile-dark)" stroke-width="{f(end_d * 0.6)}" opacity=".5"/>
      <path d="{ends}" style="stroke:var(--tile-light)" stroke-width="{f(end_d * 0.6 - 1.2)}"/>
    </g>
    <!-- The ridges, and what stands on them -->
    {hips()}
    {procession()}
    {main_ridge()}
    {chiwen()}
  </symbol>'''


START = "    <!-- roof defs: made by tools/build_roof.py -->\n"
END = "    <!-- end of roof defs -->\n"


def defs() -> str:
    _, _, _, rows = barrels()
    return (START + f'''    <clipPath id="roof-clip"><path d="{face()}"/></clipPath>
    <clipPath id="roof-under"><path d="{deep_underside()}"/></clipPath>
    <path id="roof-joints" d="{joints(rows)}"/>
    <!-- Lit from above, a concave slope brightens towards the eave, where it
         flattens out and faces the sky; a convex one would be brightest in
         the middle. -->
    <linearGradient id="roof-shade-v" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".42"/><stop offset=".3" stop-color="#000" stop-opacity=".14"/>
      <stop offset=".58" stop-color="#000" stop-opacity="0"/><stop offset=".86" stop-color="#fff" stop-opacity=".14"/>
      <stop offset="1" stop-color="#fff" stop-opacity=".04"/>
    </linearGradient>
    <linearGradient id="roof-shade-h" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity=".1"/><stop offset=".45" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".18"/>
    </linearGradient>
    <linearGradient id="ridge-cast" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".42"/><stop offset="1" stop-color="#000" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="ridge-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".4"/>
    </linearGradient>
    <linearGradient id="beast-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".16"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".3"/>
    </linearGradient>
    <radialGradient id="scroll-shade" cx=".36" cy=".32" r=".75">
      <stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".32"/>
    </radialGradient>
    <linearGradient id="chiwen-shade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff" stop-opacity=".12"/><stop offset=".5" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity=".35"/>
    </linearGradient>
    <pattern id="wear-tex" patternUnits="userSpaceOnUse" width="260" height="260">
      <image href="assets/gen/wear.webp" width="260" height="260"/>
    </pattern>
    <linearGradient id="beam-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset=".3" stop-color="#fff" stop-opacity="0"/>
      <stop offset=".75" stop-color="#000" stop-opacity=".06"/><stop offset="1" stop-color="#000" stop-opacity=".24"/>
    </linearGradient>
    <linearGradient id="age-light" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#fff3d6" stop-opacity=".07"/><stop offset=".45" stop-color="#fff3d6" stop-opacity="0"/>
      <stop offset="1" stop-color="#1a0a04" stop-opacity=".12"/>
    </linearGradient>
    <!-- The bracket sets stand back under the eave, darkest at the top -->
    <linearGradient id="dg-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".55"/><stop offset=".45" stop-color="#000" stop-opacity=".2"/>
      <stop offset="1" stop-color="#000" stop-opacity=".08"/>
    </linearGradient>
    <!-- The fanned rafters recede into shadow towards the bracket sets -->
    <linearGradient id="fan-shade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".6"/>
    </linearGradient>
''' + figure_defs() + END)


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    if START in html:
        a, b = html.index(START), html.index(END) + len(END)
    else:
        raise SystemExit("roof defs markers not found in index.html")
    html = html[:a] + defs() + html[b:]
    # Every <svg> showing the roof takes its proportions from the symbol.
    html = html.replace('class="arch-roof" viewBox="0 0 1600 210"', f'class="arch-roof" viewBox="0 0 1600 {H}"')
    start = html.index('<symbol id="roof"')
    end = html.index("</symbol>", start) + len("</symbol>")
    html = html[:start] + symbol() + html[end:]
    INDEX.write_text(html, encoding="utf-8")
    print(f"roof written (symbol {len(symbol()) // 1024} KB, defs {len(defs()) // 1024} KB)")


if __name__ == "__main__":
    main()
