# Amar RPG site

The Amar RPG as a static website: one Markdown file per page, built to plain HTML.

## Edit a page

Open `pages/<Title>.md` in any editor. The top block gives the title, the categories and, for spells, rituals and potions, the numbers shown in the stat card. The rest is Markdown.

### On the web

Every page on d6gaming.org has an "Edit this page" link. It opens the page in GitHub's editor; you need write access to this repo. Save with "Commit changes". A GitHub Action then rebuilds the site, and d6gaming.org shows the change within about five minutes.

"History" on each page lists every change. To undo one, revert that commit on GitHub.

If you also work on a local copy, run `git pull` first: the Action adds its own commits.

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
