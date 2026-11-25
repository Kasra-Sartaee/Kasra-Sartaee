#!/usr/bin/env python3
"""Render the profile card: dark_mode.svg + light_mode.svg.

Edit CONFIG, then run `python card.py` and commit the two SVGs.
No API calls, no tokens, no dependencies.
"""
from __future__ import annotations

import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- content
# A row is (key, value), None for a spacer, or ("#", title) for a section rule.
# Rows whose value is None are skipped. Every row must fit in WIDTH characters;
# the script stops with an error naming the row if one doesn't.
HEADER = "kasra@sartaee"
ROWS = [
    ("OS", "Windows + WSL2, Linux"),
    ("Host", "Dubai, UAE"),
    ("Kernel", "AI / ML Research Engineer"),
    ("IDE", "VS Code, Overleaf"),
    None,
    ("Languages.Programming", "Python, Bash"),
    ("Languages.Markup", "LaTeX, Markdown, YAML"),
    ("Languages.Real", "Persian, English"),
    None,
    ("Research.Focus", "Agentic LLMs, Program Repair, UQ"),
    ("Research.Methods", "Evolutionary & Bayesian Opt."),
    ("Stack", "PyTorch, BoTorch, pymoo, Ollama, CodeCarbon"),
    None,
    ("Education.MSc", "AI & Data Engineering, UCL"),
    ("Education.BSc", "First Class Honours, Heriot-Watt"),
    ("#", "Selected Work"),
    ("Paper.AAAI-SS", "EchoScript: script-aware music gen."),
    ("Paper.IJDSAA", "Uncertainty & information fusion"),
    ("Thesis", "apr-decoding-policy-search"),
    ("Open.Source", "econpulse"),
    ("#", "Contact"),
    ("Email", "kasrasartaee@yahoo.com"),
    ("Website", "kasrasartaee.com"),
    ("LinkedIn", None),
]
# Shown under the attractor.
CAPTION = "dx/dt=σ(y−x)  dy/dt=x(ρ−z)−y  dz/dt=xy−βz"

# --------------------------------------------------------------------------- geometry
WIDTH = 60                      # characters in the text column
FONT, LEAD = 16, 20             # text column: font size / line height (px)
ART_FONT, ART_LEAD = 9, 10.8    # attractor: smaller type for more detail
CAP_FONT = 11
CARD_W = 985
TEXT_X, ART_X, ART_W, TOP = 390, 18, 356, 34

THEMES = {
    "dark": dict(bg="#161b22", border="#30363d", text="#c9d1d9", key="#ffa657",
                 value="#a5d6ff", dots="#616e7f", art_top="#ffa657", art_bot="#a5d6ff"),
    "light": dict(bg="#f6f8fa", border="#d0d7de", text="#24292f", key="#953800",
                  value="#0a3069", dots="#afb8c1", art_top="#bc4c00", art_bot="#0550ae"),
}


# --------------------------------------------------------------------------- layout
# A line is a list of (text, css_class); class "t" is unstyled.
def kv(key: str, value: str) -> list:
    n = WIDTH - len(f". {key}:") - len(value) - 2
    if n < 2:
        raise SystemExit(f"Row '{key}: {value}' is {2 - n} character(s) too long "
                         f"for the {WIDTH}-column card. Shorten the key or value.")
    return [(". ", "t"), (key, "k"), (": ", "t"), ("." * n, "d"), (" ", "t"), (value, "v")]


def rule(title: str, lead: str) -> list:
    fill = "—" * (WIDTH - len(lead) - len(title) - 1)
    return [(lead, "t"), (title, "v" if not lead else "k"), (" " + fill, "d")]


def build_lines() -> list:
    lines = [rule(HEADER, "")]
    for row in ROWS:
        if row is None:
            lines.append([(". ", "t")])
        elif row[0] == "#":
            lines += [[], rule(row[1], "- ")]
        elif row[1] is not None:
            lines.append(kv(*row))
    return lines


# --------------------------------------------------------------------------- svg
def render(theme: str, lines: list, art: list[str]) -> str:
    c = THEMES[theme]
    text_h = TOP + (len(lines) - 1) * LEAD + 16
    art_h = (len(art) - 1) * ART_LEAD
    block_h = art_h + 26                                  # attractor + caption
    height = int(max(text_h, block_h + 2 * TOP) + 4)
    art_top = (height - block_h) / 2 + ART_FONT * 0.35
    cap_y = art_top + art_h + 26

    esc = html.escape
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{height}" '
        f'viewBox="0 0 {CARD_W} {height}" role="img" aria-labelledby="t d">',
        f'<title id="t">Kasra Sartaee</title>',
        '<desc id="d">AI / ML research engineer in Dubai. Agentic LLMs, automated program repair, '
        'uncertainty quantification. MSc AI and Data Engineering, UCL; BSc First Class Honours, '
        'Heriot-Watt. Shown beside an ASCII rendering of the Lorenz attractor.</desc>',
        "<style>",
        "text{font-family:ConsolasFallback,Consolas,'SF Mono',Menlo,'DejaVu Sans Mono',"
        f"'Courier New',monospace;font-size:{FONT}px;fill:{c['text']};white-space:pre}}",
        f".art{{font-size:{ART_FONT}px;fill:url(#g)}}",
        f".cap{{font-size:{CAP_FONT}px;fill:{c['dots']}}}",
        f".k{{fill:{c['key']}}}.v{{fill:{c['value']}}}.d{{fill:{c['dots']}}}",
        # Boot-sequence reveal. fill-mode "backwards": a renderer that ignores
        # animation still shows the finished card, never a blank one.
        "@keyframes in{from{opacity:0}to{opacity:1}}",
        ".l{animation:in .45s ease-out backwards}",
        "@media (prefers-reduced-motion:reduce){.l{animation:none}}",
        "</style>",
        f'<defs><linearGradient id="g" gradientUnits="userSpaceOnUse" x1="0" '
        f'y1="{art_top - ART_FONT:.0f}" x2="0" y2="{art_top + art_h:.0f}">'
        f'<stop offset="0" stop-color="{c["art_top"]}"/>'
        f'<stop offset="1" stop-color="{c["art_bot"]}"/></linearGradient></defs>',
        f'<rect x=".5" y=".5" width="{CARD_W - 1}" height="{height - 1}" rx="10" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>',
    ]
    for i, row in enumerate(art):
        out.append(f'<text class="art l" x="{ART_X}" y="{art_top + i * ART_LEAD:.1f}" '
                   f'xml:space="preserve" style="animation-delay:{i * 18}ms">{esc(row)}</text>')
    out.append(f'<text class="cap l" x="{ART_X + ART_W / 2:.0f}" y="{cap_y:.0f}" text-anchor="middle" xml:space="preserve" '
               f'style="animation-delay:{len(art) * 18 + 100}ms">{esc(CAPTION)}</text>')

    for i, segs in enumerate(lines):
        if not segs:
            continue
        spans = "".join(esc(t) if cls == "t" else f'<tspan class="{cls}">{esc(t)}</tspan>'
                        for t, cls in segs)
        out.append(f'<text class="l" x="{TEXT_X}" y="{TOP + i * LEAD}" xml:space="preserve" '
                   f'style="animation-delay:{200 + i * 45}ms">{spans}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main() -> None:
    art = (ROOT / "art.txt").read_text().rstrip("\n").split("\n")
    while art and not art[0].strip():
        art.pop(0)
    lines = build_lines()
    for theme in THEMES:
        (ROOT / f"{theme}_mode.svg").write_text(render(theme, lines, art))
    print("wrote dark_mode.svg, light_mode.svg")


if __name__ == "__main__":
    main()
