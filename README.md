# Amar RPG site

The Amar RPG as a static website: one Markdown file per page, built to plain HTML.

## Edit a page

Open `pages/<Title>.md` in any editor. The top block gives the title, the categories and, for spells, rituals and potions, the numbers shown in the stat card. The rest is Markdown.

## Build

```
python3 build.py
```

This writes `site/*.html` and `site/search.json`. The `site/` folder is what the web server serves. Pictures live in `site/images/`, fonts, style and search in `site/theme/`.

## Files

- `pages/`: the pages
- `nav.yaml`: the menu
- `template.html`: the frame around every page
- `build.py`: the build
- `tools/import_wiki.py`: the one-off import from the old wiki
- `tools/shots.js`: screenshots at desktop and phone size, for checking the design
