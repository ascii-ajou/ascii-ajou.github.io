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
import html
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


# Research keywords: each label is counted over paper titles (conference, journal, under review).
# Counts update automatically; add a row here when the lab starts a new topic.
KEYWORDS = [
    ("Processing-in-Memory", r"processing[- ]in[- ]memory|\bPIM\b|in-memory|프로세싱.?인.?메모리"),
    ("AI / DNN Acceleration", r"neural|\bDNN\b|\bGNN\b|machine learning|quantization|embedding|\bAI\b"),
    ("Memory & Cache Systems", r"DRAM|cache|memory access|heterogeneous memory|3D-Stacked|page table"),
    ("Processors (CPU/GPU/NPU)", r"\bCPUs?\b|\bGPUs?\b|\bNPUs?\b|processor|processing unit|multicore|\bMAC unit"),
    ("Heterogeneous Computing", r"heterogeneous|multicore|multi-GPU"),
    ("Robotics & Embodied AI", r"robot"),
    ("Recommendation Systems", r"recommendation"),
    ("Scheduling & Serving", r"scheduling|serving|execution scheme"),
    ("Error Correction Codes", r"error correction|\bBCH\b"),
]


def titles(chunk):
    return [html.unescape(t) for t in re.findall(r'<span class="title">"?(.*?)"?</span>', chunk)]


def count_pubs():
    page = open(PUBS, encoding="utf-8").read()
    conf, jour = section(page, "Conference Papers"), section(page, "Journal Papers")
    review = section(page, "Under Review")
    n = lambda s, pat=r"<li>": len(re.findall(pat, s))
    paper_titles = titles(conf) + titles(jour) + titles(review)
    kw = [(label, sum(1 for t in paper_titles if re.search(pat, t, re.I))) for label, pat in KEYWORDS]
    kw = sorted([k for k in kw if k[1]], key=lambda k: -k[1])[:6]  # top 6 topics
    conf_items = re.findall(r"<li>.*?</li>", conf, re.S)
    jour_items = re.findall(r"<li>.*?</li>", jour, re.S)
    has = lambda li, cls: f'class="tag {cls}"' in li
    is_kci = lambda li: not has(li, "sci") and re.search(r'<span class="where">[^<]*(Korea|[\uac00-\ud7a3])', li)
    return {
        "papers": len(conf_items) + len(jour_items),
        "patents": n(section(page, "Patent Applications")) + n(section(page, "Patent Registrations")),
        # Conference indexes can overlap (a paper may be both BK21+ IF4 and KIISE); Others = neither
        "conf_bk": sum(has(li, "bk") for li in conf_items),
        "conf_kiise": sum(has(li, "kiise") for li in conf_items),
        "conf_other": sum(not has(li, "bk") and not has(li, "kiise") for li in conf_items),
        "jour_scie": sum(has(li, "sci") for li in jour_items),
        "jour_kci": sum(bool(is_kci(li)) for li in jour_items),
        "jour_other": sum(not has(li, "sci") and not is_kci(li) for li in jour_items),
        "keywords": kw,
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
    num = lambda v: f'<span class="num" data-count="{v}">{v}</span>'
    tile = lambda inner, l: f'          <div class="stat"><span class="lbl">{l}</span>{inner}</div>'
    row = lambda name, items: (f'          <div class="stats stats-sub"><span class="row-lbl">{name}</span>\n'
                               + "\n".join("  " + tile(num(v), l) for v, l in items) + "\n          </div>")
    main_tiles = row("Total", [(s["citations"], "Citations"), (c["papers"], "Papers"), (c["patents"], "Patents")]) \
        .replace("stats stats-sub", "stats stats-main", 1)
    sub_tiles = row("Conference", [(c["conf_bk"], "BK21+"), (c["conf_kiise"], "KIISE"), (c["conf_other"], "Others")]) + "\n" + \
        row("Journal", [(c["jour_scie"], "SCIE"), (c["jour_kci"], "KCI"), (c["jour_other"], "Others")])
    top = c["keywords"][0][1] if c["keywords"] else 1
    kw_html = "\n".join(
        f'          <li style="--w:{round(n / top * 100)}%"><span class="k">{html.escape(k)}</span>'
        f'<span class="c" data-count="{n}">{n}</span></li>' for k, n in c["keywords"])
    return f"""{START}
  <section class="alt">
    <div class="container">
      <h2 class="section-title">Research Impact</h2>
      <div class="impact" data-animate>
        <div class="stats-wrap">
{main_tiles}
          <div class="stats-group">
{sub_tiles}
          </div>
        </div>
        <figure class="cite-chart">
          <figcaption>Citations per year</figcaption>
          <ol class="bars">
{chr(10).join(bars)}
          </ol>
        </figure>
      </div>
      <div class="keywords" data-animate>
        <h3>Research Keywords <span>papers per topic</span></h3>
        <ul>
{kw_html}
        </ul>
      </div>
      <p class="note">Citation metrics from <a href="https://scholar.google.com/citations?user={SCHOLAR_USER}" target="_blank" rel="noopener">Google Scholar</a> (refreshed daily). Paper, patent and keyword counts from <a href="publications.html">Publications</a>.</p>
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
