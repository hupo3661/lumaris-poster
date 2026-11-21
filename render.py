#!/usr/bin/env python3
"""Render the LUMARIS travel poster to entry.png.

A travel poster for LUMARIS, a place that does not exist: a golden-hour
isle where the sea lies flat as glass, and one great natural stone arch
(the Glass Arch) frames the setting sun. Everything is drawn from scratch
with Pillow: gradients, shapes and letters only. No photographs, no
downloaded images, no network, no clock, no randomness beyond a fixed seed.

Deterministic: two runs produce byte-identical PNGs.
"""

import hashlib
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"

W, H = 768, 1024          # final poster size
S = 2                     # supersample factor
W2, H2 = W * S, H * S
HORIZON = 600             # sea line, in final coordinates
SUN = (384, 556)          # sun centre, in final coordinates
SEED = 11


def _font(name, size):
    """Load a bundled font, falling back to the system copy."""
    for path in (ASSETS / name,
                 Path("/usr/share/fonts/truetype/dejavu") / name):
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def _vgrad(width, height, stops):
    """Vertical gradient. stops: list of (position 0..1, (r, g, b))."""
    img = Image.new("RGB", (1, height))
    px = img.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                px[0, y] = _lerp(c0, c1, (t - p0) / (p1 - p0 or 1))
                break
        else:
            px[0, y] = stops[-1][1]
    return img.resize((width, height))


def _pts(points):
    return [(x * S, y * S) for x, y in points]


def render():
    img = Image.new("RGB", (W2, H2))
    d = ImageDraw.Draw(img, "RGBA")

    # --- sky: deep teal dawn at the top, melting to gold at the horizon ---
    sky = _vgrad(W2, HORIZON * S, [
        (0.00, (13, 52, 60)),
        (0.38, (43, 104, 110)),
        (0.68, (214, 141, 82)),
        (1.00, (248, 203, 122)),
    ])
    img.paste(sky, (0, 0))

    # --- soft clouds (blurred layer, fixed positions) ---
    clouds = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    cd = ImageDraw.Draw(clouds)
    for cx, cy, rx, ry, alpha in [
        (180, 150, 150, 16, 46), (560, 120, 170, 14, 40),
        (420, 250, 190, 15, 52), (120, 330, 120, 12, 36),
        (660, 300, 130, 13, 42),
    ]:
        cd.ellipse([(cx - rx) * S, (cy - ry) * S,
                    (cx + rx) * S, (cy + ry) * S],
                   fill=(255, 236, 200, alpha))
    clouds = clouds.filter(ImageFilter.GaussianBlur(18 * S))
    img.paste(clouds, (0, 0), clouds)

    # --- sun glow, then the sun itself ---
    glow = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r, a in [(260, 18), (200, 26), (150, 40), (110, 60)]:
        gd.ellipse([(SUN[0] - r) * S, (SUN[1] - r) * S,
                    (SUN[0] + r) * S, (SUN[1] + r) * S],
                   fill=(255, 214, 130, a))
    glow = glow.filter(ImageFilter.GaussianBlur(12 * S))
    img.paste(glow, (0, 0), glow)
    d.ellipse([(SUN[0] - 62) * S, (SUN[1] - 62) * S,
               (SUN[0] + 62) * S, (SUN[1] + 62) * S],
              fill=(255, 238, 176, 255))

    # --- sea: gold at the horizon, deep teal at the bottom ---
    sea = _vgrad(W2, (H - HORIZON) * S, [
        (0.00, (240, 178, 94)),
        (0.25, (122, 158, 138)),
        (1.00, (13, 55, 64)),
    ])
    img.paste(sea, (0, HORIZON * S))

    # --- sun path: shimmering gold dashes on the water (fixed seed) ---
    rng = random.Random(SEED)
    for i in range(46):
        y = HORIZON + 14 + i * 8.5
        depth = (y - HORIZON) / (H - HORIZON)
        half = 52 * (1 - depth * 0.55) + rng.uniform(-8, 8)
        cx = SUN[0] + rng.uniform(-14, 14) * depth
        alpha = int(150 * (1 - depth * 0.75))
        d.line([(cx - half) * S, y * S, (cx + half) * S, y * S],
               fill=(255, 226, 150, alpha), width=max(2, int(5 * S * (1 - depth * 0.5))))

    # --- faint wave lines ---
    for y, alpha in [(660, 40), (730, 34), (820, 30), (920, 26)]:
        d.line([(40 * S, y * S), (728 * S, y * S)],
               fill=(255, 240, 200, alpha), width=2 * S)

    # --- the Glass Arch: one stone arch rising from the sea, sun in its eye ---
    stone = (74, 50, 38, 255)
    rim = (232, 160, 92, 255)
    d.arc([168 * S, 296 * S, 600 * S, 780 * S], start=180, end=360,
          fill=stone, width=64 * S)
    d.arc([232 * S, 360 * S, 536 * S, 716 * S], start=180, end=360,
          fill=rim, width=7 * S)
    d.polygon(_pts([(148, 712), (168, 538), (232, 538), (222, 712)]), fill=stone)
    d.polygon(_pts([(620, 712), (600, 538), (536, 538), (546, 712)]), fill=stone)
    # sunlit edge on the right pillar
    d.line([(540 * S, 545 * S), (550 * S, 708 * S)], fill=rim, width=5 * S)
    # rocky texture on the arch band: fixed-seed speckles along its curve
    rng2 = random.Random(SEED + 1)
    import math
    for _ in range(55):
        ang = math.radians(rng2.uniform(182, 358))
        rr = rng2.uniform(170, 198)
        px = 384 + rr * math.cos(ang)
        py = 538 + rr * math.sin(ang) * (242 / 216)
        w = rng2.uniform(2, 6)
        col = (52, 34, 26, 90) if rng2.random() < 0.6 else (150, 98, 58, 80)
        d.ellipse([(px - w) * S, (py - w * 0.6) * S,
                   (px + w) * S, (py + w * 0.6) * S], fill=col)
    # water shadow at the pillar bases
    for cx in (186, 582):
        d.ellipse([(cx - 52) * S, 706 * S, (cx + 52) * S, 722 * S],
                  fill=(10, 40, 46, 110))

    # --- headlands left and right, with cypress trees on the left ---
    cliff = (18, 46, 51, 255)
    d.polygon(_pts([(0, 1024), (0, 768), (96, 726), (190, 742),
                    (228, 800), (196, 1024)]), fill=cliff)
    d.polygon(_pts([(768, 1024), (768, 806), (668, 772), (606, 806),
                    (640, 862), (668, 1024)]), fill=cliff)
    for tx, th in [(52, 64), (86, 84), (122, 58)]:
        d.ellipse([(tx - 9) * S, (742 - th) * S,
                   (tx + 9) * S, 742 * S], fill=(12, 34, 38, 255))

    # --- a small white sailboat, heading for the arch ---
    bx, by = 268, 818
    d.polygon(_pts([(bx, by - 52), (bx, by - 6), (bx + 34, by - 6)]),
              fill=(255, 250, 235, 255))
    d.polygon(_pts([(bx - 4, by - 44), (bx - 4, by - 6), (bx - 30, by - 6)]),
              fill=(238, 228, 205, 255))
    d.polygon(_pts([(bx - 34, by - 4), (bx + 38, by - 4),
                    (bx + 30, by + 8), (bx - 26, by + 8)]), fill=(30, 24, 20, 255))
    d.ellipse([(bx - 30) * S, (by + 12) * S,
               (bx + 34) * S, (by + 20) * S], fill=(255, 226, 150, 70))

    # --- birds ---
    for bx2, by2, s in [(150, 210, 12), (196, 182, 9), (612, 168, 11),
                        (648, 205, 8), (560, 232, 7)]:
        d.arc([(bx2 - s) * S, (by2 - s // 2) * S,
               bx2 * S, (by2 + s // 2) * S], start=200, end=340,
              fill=(30, 32, 30, 220), width=3 * S)
        d.arc([bx2 * S, (by2 - s // 2) * S,
               (bx2 + s) * S, (by2 + s // 2) * S], start=200, end=340,
              fill=(30, 32, 30, 220), width=3 * S)

    # --- the place name, large in the sky; the poster's only words ---
    title = "LUMARIS"
    font = _font("DejaVuSerif-Bold.ttf", 96 * S)
    tracking = 10 * S
    widths = [d.textlength(ch, font=font) for ch in title]
    total = sum(widths) + tracking * (len(title) - 1)
    x = (W2 - total) / 2
    y = 66 * S
    cream = (255, 243, 214, 255)
    shadow = (20, 40, 48, 130)
    for i, ch in enumerate(title):
        for ox, oy, col in ((4 * S, 5 * S, shadow), (0, 0, cream)):
            d.text((x + ox, y + oy), ch, font=font, fill=col)
        x += widths[i] + tracking

    # --- small diamond ornament under the name ---
    cx, cy, r = 384, 216, 9
    d.polygon(_pts([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]),
              fill=(255, 243, 214, 235))
    d.line([(150 * S, cy * S), (352 * S, cy * S)],
           fill=(255, 243, 214, 200), width=2 * S)
    d.line([(416 * S, cy * S), (618 * S, cy * S)],
           fill=(255, 243, 214, 200), width=2 * S)

    # --- thin double border frame ---
    d.rectangle([16 * S, 16 * S, (W - 16) * S, (H - 16) * S],
                outline=(255, 243, 214, 210), width=3 * S)
    d.rectangle([28 * S, 28 * S, (W - 28) * S, (H - 28) * S],
                outline=(255, 243, 214, 130), width=1 * S)

    img = img.convert("RGB").resize((W, H), Image.LANCZOS)
    return img


def main():
    out = HERE / "entry.png"
    img = render()
    img.save(out, "PNG", optimize=True)
    data = out.read_bytes()
    print(f"wrote {out} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    assert len(data) <= 1_048_576, "over 1 MiB"
    assert img.size == (W, H)
    return 0


if __name__ == "__main__":
    sys.exit(main())
