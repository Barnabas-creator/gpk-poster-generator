Weekly Church Poster Generator
================================
Generates the "Ibadah Minggu" invitation poster for the upcoming Sunday.

Usage:
  python3 generate.py [YYYY-MM-DD]
  (date = target Sunday; defaults to "the next Sunday from today")

Requires: pip install playwright --break-system-packages ; then a Chromium
build reachable by Playwright (set PLAYWRIGHT_BROWSERS_PATH if using a
shared cache, e.g. /opt/pw-browsers on the Claude cloud workspace).

Rotation rule:
  background theme = ISO week number of the target Sunday mod 4  (weekly)
  layout structure  = month number of the target Sunday mod 3    (monthly)

Output: output/<YYYY-M-D>.png

This folder is self-contained (fonts + logo assets included) and does not
need network access to render.
