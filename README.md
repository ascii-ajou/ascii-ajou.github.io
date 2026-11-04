# ASCII Lab Homepage

ASCII Lab (Architectures, Systems, and Computing for Intelligence Innovations), Ajou University.

Plain HTML/CSS static site — no build step. Works directly on GitHub Pages.

## Structure
- `index.html` — Home (intro, recruiting, news, research interests, selected publications)
- `professor.html`, `members.html`, `research.html`, `publications.html`, `contact.html`
- `assets/css/style.css` — all styles (colors at the top, `:root`)
- `assets/img/` — logo, photos, research figures

## Local preview
```
python3 -m http.server 8000
```
Open http://localhost:8000

## Deploy (GitHub Pages)
1. Push to `ascii-ajou/ascii-ajou.github.io` → served at https://ascii-ajou.github.io/
2. Settings → Pages → Source: `main` branch, `/ (root)`.

## Updating CSS/JS
Browsers cache assets for ~10 min. After changing `style.css` or `main.js`, bump the `?v=N` query in every HTML page.

## Research Impact statistics (Home)
`index.html` has a generated block between `<!-- STATS:START -->` and `<!-- STATS:END -->`.
- `scripts/update_stats.py` pulls citations / h-index / i10-index / citations-per-year from
  Google Scholar (Hongju Kal) and counts papers, top-tier conferences, SCIE journals and patents
  from `publications.html`. If Scholar blocks the request, the last values in
  `scripts/scholar-cache.json` are reused.
- `scripts/daily_stats.sh` runs it daily from cron on the lab server and pushes only when values change:
  `0 6 * * * /home2/hongju/CLAUDE/HOME_PAGE/scripts/daily_stats.sh >> /home2/hongju/CLAUDE/HOME_PAGE/scripts/daily_stats.log 2>&1`
- Don't edit the block by hand; run `python3 scripts/update_stats.py` after changing publications.
