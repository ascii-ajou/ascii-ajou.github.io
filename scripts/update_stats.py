#!/usr/bin/env python3
"""Refresh the "Research Impact" block on index.html.

- Citation metrics come from Google Scholar (Hongju Kal, user=mmae918AAAAJ).
- Publication / patent counts are counted from publications.html.

The block lives between <!-- STATS:START --> and <!-- STATS:END --> in index.html.
If Scholar can't be reached (e.g. rate-limited), the last values saved in
scripts/scholar-cache.json are reused, so the page never loses its numbers.

Run from anywhere:  python3 scripts/update_stats.py
scripts/daily_stats.sh runs this once a day from cron and pushes when values change.
"""
import datetime
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHOLAR_USER = "mmae918AAAAJ"
SCHOLAR_URL = f"https://scholar.google.com/citations?user={SCHOLAR_USER}&hl=en&pagesize=100"
CACHE = os.path.join(ROOT, "scripts", "scholar-cache.json")
INDEX = os.path.join(ROOT, "index.html")
PUBS = os.path.join(ROOT, "publications.html")
START, END = "<!-- STATS:START -->", "<!-- STATS:END -->"


def fetch_scholar():
    req = urllib.request.Request(SCHOLAR_URL, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept-Language": "en-US,en",
    })
    page = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    std = [int(x) for x in re.findall(r'class="gsc_rsb_std">(\d+)', page)]
    if len(std) < 6:
        raise ValueError("citation table not found (blocked or layout changed)")
    # Year labels and bars are positioned by their CSS "right" offset; zero years have no bar.
    years = [(int(r), int(y)) for r, y in re.findall(r'class="gsc_g_t" style="right:(\d+)px">(\d{4})', page)]
    bars = [(int(r), int(v)) for r, v in re.findall(
        r'class="gsc_g_a" style="right:(\d+)px[^"]*"[^>]*><span class="gsc_g_al">(\d+)', page)]
    per_year = {y: 0 for _, y in years}
    for r, v in bars:
        nearest = min(years, key=lambda ry: abs(ry[0] - r))
        per_year[nearest[1]] = v
    return {
        "citations": std[0], "h_index": std[2], "i10_index": std[4],
        "per_year": {str(y): per_year[y] for y in sorted(per_year)},
        "fetched": datetime.date.today().isoformat(),
    }


def section(page, title):
    m = re.search(r'<h2 class="section-title">' + re.escape(title) + r'</h2>(.*?)</ul>', page, re.S)
    return m.group(1) if m else ""


def count_pubs():
    page = open(PUBS, encoding="utf-8").read()
    conf, jour = section(page, "Conference Papers"), section(page, "Journal Papers")
    n = lambda s, pat=r"<li>": len(re.findall(pat, s))
    return {
        "papers": n(conf) + n(jour),
        "top_conf": n(conf, r'class="tag bk"'),
        "scie": n(jour, r'class="tag sci"'),
        "patents": n(section(page, "Patent Applications")) + n(section(page, "Patent Registrations")),
    }


def render(s, c):
    per_year = s["per_year"]
    peak = max(per_year.values()) or 1
    this_year = str(datetime.date.today().year)
    bars = []
    for y, v in per_year.items():
        h = max(round(v / peak * 100), 2 if v else 0)
        cls = "bar ytd" if y == this_year else "bar"
        lab = f"{y}: {v} citation{'s' if v != 1 else ''}" + (" (so far)" if y == this_year else "")
        val = f'<span class="v">{v}</span>' if v == peak else ""
        bars.append(f'          <li class="{cls}" style="--h:{h}%" tabindex="0" aria-label="{lab}" data-tip="{lab}">'
                    f'{val}<span class="b"></span><span class="y">&rsquo;{y[2:]}</span></li>')
    tiles = [
        (s["citations"], "Citations"), (s["h_index"], "h-index"), (s["i10_index"], "i10-index"),
        (c["papers"], "Papers"), (c["top_conf"], "Top-Tier Conf."), (c["scie"], "SCIE Journals"),
        (c["patents"], "Patents"),
    ]
    tile_html = "\n".join(f'          <div class="stat"><span class="num">{v}</span><span class="lbl">{l}</span></div>'
                          for v, l in tiles)
    return f"""{START}
  <section class="alt">
    <div class="container">
      <h2 class="section-title">Research Impact</h2>
      <div class="impact">
        <div class="stats">
{tile_html}
        </div>
        <figure class="cite-chart">
          <figcaption>Citations per year</figcaption>
          <ol class="bars">
{chr(10).join(bars)}
          </ol>
        </figure>
      </div>
      <p class="note">Citation metrics from <a href="https://scholar.google.com/citations?user={SCHOLAR_USER}" target="_blank" rel="noopener">Google Scholar</a> (refreshed daily). Paper and patent counts from <a href="publications.html">Publications</a>.</p>
    </div>
  </section>
  {END}"""


def main():
    try:
        stats = fetch_scholar()
        json.dump(stats, open(CACHE, "w"), indent=2)
        print(f"[stats] Google Scholar: {stats['citations']} citations, h={stats['h_index']}, i10={stats['i10_index']}")
    except Exception as e:  # keep last good values
        if not os.path.exists(CACHE):
            print(f"[stats] Scholar fetch failed and no cache: {e}", file=sys.stderr)
            return 0
        stats = json.load(open(CACHE))
        print(f"[stats] Scholar fetch failed ({e}); using cached values from {stats['fetched']}", file=sys.stderr)
    counts = count_pubs()
    page = open(INDEX, encoding="utf-8").read()
    a, b = page.find(START), page.find(END)
    if a < 0 or b < 0:
        print("[stats] markers not found in index.html", file=sys.stderr)
        return 0
    new = page[:a] + render(stats, counts) + page[b + len(END):]
    if new != page:
        open(INDEX, "w", encoding="utf-8").write(new)
        print("[stats] index.html updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
