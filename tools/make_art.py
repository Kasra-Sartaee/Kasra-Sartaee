"""Generate the ASCII art panel for the profile card.

Default: the Lorenz attractor (x-z projection) -- the textbook object behind the
limits of deterministic forecasting, i.e. why forecasts should be probabilistic.
Alternative: --photo path/to/headshot.jpg converts a portrait instead.

    python tools/make_art.py                 # Lorenz attractor -> art.txt
    python tools/make_art.py --photo me.jpg  # portrait      -> art.txt
"""
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

COLS, ROWS = 66, 44         # art is set in a smaller font than the text column
CHAR_ASPECT = 0.6 * 9 / 10.8   # glyph width / line height (9px mono, 10.8px leading)
ANGLE = 0.0               # rotation about z before projecting; 0 = classic x-z view
RAMP = " .,:;i1tfLCG08@"


def to_ascii(img: Image.Image, invert: bool = False, gamma: float = 1.0) -> list[str]:
    img = img.convert("L").resize((COLS, ROWS), Image.LANCZOS)
    a = np.asarray(img, dtype=np.float32) / 255.0
    if invert:
        a = 1.0 - a
    a = np.clip(a, 0, 1) ** gamma
    idx = np.round(a * (len(RAMP) - 1)).astype(int)
    return ["".join(RAMP[i] for i in row).rstrip() for row in idx]


def lorenz(steps: int = 9000, dt: float = 0.005, transient: int = 1500) -> Image.Image:
    """Thin-trajectory render of the Lorenz attractor (sigma=10, rho=28, beta=8/3), x-z view.

    A single ~45-time-unit orbit rather than a long-run density: at ASCII resolution a
    density cloud collapses into a blob, while ~30 discrete loops keep the spiral
    structure and the two empty "eyes" that make it recognisable.
    """
    s, r, b = 10.0, 28.0, 8.0 / 3.0
    f = lambda v: np.array([s * (v[1] - v[0]), v[0] * (r - v[2]) - v[1], v[0] * v[1] - b * v[2]])
    v, pts = np.array([1.0, 1.0, 1.0]), []
    for i in range(steps + transient):                  # RK4
        k1 = f(v); k2 = f(v + dt / 2 * k1); k3 = f(v + dt / 2 * k2); k4 = f(v + dt * k3)
        v = v + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if i >= transient:
            pts.append(v)
    P = np.array(pts)
    a = np.deg2rad(ANGLE)
    X = P[:, 0] * np.cos(a) - P[:, 1] * np.sin(a)
    Z = P[:, 2]
    W = 1200; H = int(W * ROWS / (COLS * CHAR_ASPECT))   # canvas matches the glyph grid's aspect
    span = max((X.max() - X.min()) / W, (Z.max() - Z.min()) / H) * 1.06
    px = (X - (X.max() + X.min()) / 2) / span + W / 2
    pz = H / 2 - (Z - (Z.max() + Z.min()) / 2) / span
    im = Image.new("L", (W, H)); ImageDraw.Draw(im).line(list(zip(px, pz)), fill=255, width=4)
    return im.filter(ImageFilter.GaussianBlur(1.6))


def portrait(path: str) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(path)).convert("L")
    w, h = img.size
    target = COLS * CHAR_ASPECT / ROWS          # width/height of the character grid
    if w / h > target:                          # centre-crop to grid aspect
        nw = int(h * target); img = img.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target); img = img.crop((0, 0, w, nh))
    img = ImageOps.autocontrast(img, cutoff=2)
    return img


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", help="headshot to convert instead of the attractor")
    ap.add_argument("--out", default="art.txt")
    a = ap.parse_args()
    lines = to_ascii(portrait(a.photo), gamma=1.1) if a.photo else to_ascii(lorenz(), gamma=0.7)
    with open(a.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
