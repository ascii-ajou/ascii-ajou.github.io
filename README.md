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
