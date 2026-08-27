#!/usr/bin/env python3
"""
Weekly church poster generator.
Usage: python3 generate.py [YYYY-MM-DD]   (date = the target Sunday; defaults to "next Sunday from today")
Outputs: output/<YYYY-M-D>.png  (e.g. output/2026-8-30.png)

Rotation rule:
  background theme  = ISO week number of the target Sunday  mod 4
  layout structure   = month number of the target Sunday     mod 3
This means the background changes every week, and the overall layout (arrangement)
changes every month, exactly as requested.
"""
import sys, os, datetime, pathlib, base64
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent.resolve()
ASSETS = ROOT / "assets"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

INDO_MONTHS = ["", "Januari","Februari","Maret","April","Mei","Juni",
               "Juli","Agustus","September","Oktober","November","Desember"]

# ---------------------------------------------------------------- themes ----
THEMES = [
  { # 0 Sand — warm cream, terracotta accent, subtle diagonal weave
    "vars": {
      "--bg-base":"#f3e6cf","--ink":"#33220f","--accent":"#9c5a2c","--sub":"#7a5c42",
      "--panel":"#fffaf0","--line":"#c9a15a","--panel-soft":"rgba(255,252,242,.5)",
      "--quote":"#241a12",
      "--blob1":"#e0c79c","--blob2":"#efdcbc","--blob-bottom":"#3a2a1c","--on-blob":"#f9f1e2",
      "--on-blob-accent":"#e2b878",
    },
    "logo":"logo_forest.png",
    "bg_layer": """
      <svg class="bglayer" width="1200" height="1500" style="position:absolute;inset:0;opacity:.55">
        <defs>
          <pattern id="weave" width="46" height="46" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="46" stroke="#b8863f" stroke-opacity=".18" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="1200" height="1500" fill="url(#weave)"/>
      </svg>
    """,
  },
  { # 1 Honey — warm wheat / amber wash
    "vars": {
      "--bg-base":"#f7ecd6","--ink":"#3a2a12","--accent":"#96632a","--sub":"#7d6544",
      "--panel":"#fffaf1","--line":"#c9a15a","--panel-soft":"rgba(255,251,243,.55)",
      "--quote":"#2a1d0e",
      "--blob1":"#e6cd9c","--blob2":"#f3e4c6","--blob-bottom":"#3a2a12","--on-blob":"#f9f2e2",
      "--on-blob-accent":"#e3bb7a",
    },
    "logo":"logo_forest.png",
    "bg_layer": """
      <svg width="1200" height="1500" style="position:absolute;inset:0">
        <defs>
          <radialGradient id="wash1" cx="15%" cy="10%" r="55%">
            <stop offset="0%" stop-color="#e8cd9a" stop-opacity=".7"/>
            <stop offset="100%" stop-color="#e8cd9a" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="wash2" cx="90%" cy="85%" r="50%">
            <stop offset="0%" stop-color="#d9ab63" stop-opacity=".45"/>
            <stop offset="100%" stop-color="#d9ab63" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <rect width="1200" height="1500" fill="url(#wash1)"/>
        <rect width="1200" height="1500" fill="url(#wash2)"/>
      </svg>
    """,
  },
  { # 2 Blush — dusty rose / terracotta gradient
    "vars": {
      "--bg-base":"#f6e8de","--ink":"#3a2620","--accent":"#a94f26","--sub":"#8a6656",
      "--panel":"#fffaf5","--line":"#c98a5e","--panel-soft":"rgba(255,250,246,.55)",
      "--quote":"#2e1c14",
      "--blob1":"#e8bda4","--blob2":"#f3dccb","--blob-bottom":"#3a2620","--on-blob":"#f9ece1",
      "--on-blob-accent":"#eab48d",
    },
    "logo":"logo_forest.png",
    "bg_layer": """
      <svg width="1200" height="1500" style="position:absolute;inset:0">
        <defs>
          <radialGradient id="wb1" cx="85%" cy="8%" r="55%">
            <stop offset="0%" stop-color="#e8bda4" stop-opacity=".6"/>
            <stop offset="100%" stop-color="#e8bda4" stop-opacity="0"/>
          </radialGradient>
          <radialGradient id="wb2" cx="8%" cy="95%" r="55%">
            <stop offset="0%" stop-color="#d68f66" stop-opacity=".42"/>
            <stop offset="100%" stop-color="#d68f66" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <rect width="1200" height="1500" fill="url(#wb1)"/>
        <rect width="1200" height="1500" fill="url(#wb2)"/>
      </svg>
    """,
  },
  { # 3 Ember — warm deep espresso with gold light rays
    "vars": {
      "--bg-base":"#241611","--ink":"#f8ead4","--accent":"#e0a95f","--sub":"#d6bfa2",
      "--panel":"rgba(255,240,215,.12)","--line":"#e0a95f","--panel-soft":"rgba(255,240,215,.08)",
      "--quote":"#fdf3e2",
      "--blob1":"#4d3122","--blob2":"#33201a","--blob-bottom":"#17100c","--on-blob":"#f8ead4",
      "--on-blob-accent":"#e0a95f",
    },
    "logo":"logo_gold.png",
    "bg_layer": """
      <svg width="1200" height="1500" style="position:absolute;inset:0">
        <defs>
          <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#3a2318"/>
            <stop offset="55%" stop-color="#241611"/>
            <stop offset="100%" stop-color="#160d09"/>
          </linearGradient>
          <radialGradient id="glow" cx="50%" cy="18%" r="45%">
            <stop offset="0%" stop-color="#e0a95f" stop-opacity=".4"/>
            <stop offset="100%" stop-color="#e0a95f" stop-opacity="0"/>
          </radialGradient>
        </defs>
        <rect width="1200" height="1500" fill="url(#sky)"/>
        <rect width="1200" height="1500" fill="url(#glow)"/>
        <g stroke="#e0a95f" stroke-opacity=".14">
          <line x1="600" y1="0" x2="120" y2="900"/>
          <line x1="600" y1="0" x2="360" y2="1000"/>
          <line x1="600" y1="0" x2="600" y2="1050"/>
          <line x1="600" y1="0" x2="840" y2="1000"/>
          <line x1="600" y1="0" x2="1080" y2="900"/>
        </g>
      </svg>
    """,
  },
]

# ---------------------------------------------------------------- layouts ----
CROSS_SVG = ('<svg class="cross" viewBox="0 0 56 130" fill="none" xmlns="http://www.w3.org/2000/svg">'
             '<rect x="22" y="0" width="12" height="130" fill="currentColor" opacity=".55"/>'
             '<rect x="0" y="34" width="56" height="12" fill="currentColor" opacity=".55"/>'
             '</svg>')

LAYOUTS = [
  { # 0 Arch
    "class": "layout-arch",
    "decor": f'<div class="arch-shape"></div><div class="arch-outline"></div>'
             f'<div style="position:absolute;left:50%;top:268px;transform:translateX(-50%);color:var(--line)">{CROSS_SVG}</div>'
             f'<div class="dots">&middot; &nbsp; &middot; &nbsp; &middot;</div>',
  },
  { # 1 Blob / organic
    "class": "layout-blob",
    "decor": '<div class="blob1"></div><div class="blob2"></div><div class="bigblob"></div>',
  },
  { # 2 Elegant frame
    "class": "layout-frame",
    "decor": ('<div class="frame"></div>'
              '<div class="corner c-tl"></div><div class="corner c-tr"></div>'
              '<div class="corner c-bl"></div><div class="corner c-br"></div>'),
  },
]

def next_sunday(from_date: datetime.date) -> datetime.date:
    days_ahead = (6 - from_date.weekday()) % 7  # Monday=0 ... Sunday=6
    if days_ahead == 0:
        days_ahead = 7
    return from_date + datetime.timedelta(days=days_ahead)

def build_html(target: datetime.date) -> str:
    week_idx = target.isocalendar().week % len(THEMES)
    month_idx = target.month % len(LAYOUTS)
    theme = THEMES[week_idx]
    layout = LAYOUTS[month_idx]

    date_str = f"Minggu, {target.day} {INDO_MONTHS[target.month]} {target.year}"

    html = (ROOT / "poster.html").read_text(encoding="utf-8")
    var_style = ";".join(f"{k}:{v}" for k, v in theme["vars"].items())
    html = html.replace('class="page LAYOUT_CLASS BG_CLASS"',
                         f'class="page {layout["class"]}" style="{var_style}"')
    html = html.replace("BG_LAYER", theme["bg_layer"])
    html = html.replace("LAYOUT_DECOR", layout["decor"])
    logo_path = (ASSETS / theme["logo"]).resolve()
    logo_b64 = base64.b64encode(logo_path.read_bytes()).decode("ascii")
    html = html.replace("LOGO_SRC", f"data:image/png;base64,{logo_b64}")
    html = html.replace("DATE_STR", date_str)
    return html, week_idx, month_idx

def render(html: str, out_path: pathlib.Path):
    render_file = ROOT / "_render.html"
    render_file.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
        browser = p.chromium.launch(executable_path=exe if pathlib.Path(exe).exists() else None)
        page = browser.new_page(viewport={"width":1200, "height":1500}, device_scale_factor=2)
        page.goto(render_file.as_uri(), wait_until="networkidle")
        page.screenshot(path=str(out_path))
        browser.close()
    render_file.unlink(missing_ok=True)

def main():
    if len(sys.argv) > 1:
        target = datetime.date.fromisoformat(sys.argv[1])
    else:
        target = next_sunday(datetime.date.today())

    html, week_idx, month_idx = build_html(target)
    fname = f"{target.year}-{target.month}-{target.day}.png"
    out_path = OUT / fname
    render(html, out_path)
    print(f"Target Sunday: {target.isoformat()}")
    print(f"Theme index (week % 4): {week_idx}")
    print(f"Layout index (month % 3): {month_idx}")
    print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
