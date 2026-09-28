#!/usr/bin/env python3
"""One-off import: the cached wiki export in ~/Main/G/AMAR/Book/src
becomes pages/*.md, and the images those pages use go to site/images/.

After the switch the Markdown files are the source, so this only runs
again to redo the import from scratch.
"""
import json, pathlib, re, subprocess, sys, urllib.parse
import yaml
from bs4 import BeautifulSoup
from PIL import Image

BOOK = pathlib.Path.home() / "Main/G/AMAR/Book"
SRC, WIKI_IMG = BOOK / "src", BOOK / "img/wiki"
ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES, IMAGES = ROOT / "pages", ROOT / "site/images"
WIKI = "https://d6gaming.org/index.php/"

P = json.load(open(SRC / "pages.json"))
CATS, TITLES = P["cats"], P["titles"]


def cat(c):
    return sorted(t for t in TITLES if c in CATS.get(t, []) and not t.startswith("Legacy"))


RULES = ["Introduction", "Amar rules 101", "The Character", "Advantages and Disadvantages",
         "Playable Races", "Half Elf", "Lizard Man (Playable Race)", "Trollkin (Playable Race)",
         "Combat", "Movement and Weather", "Equipment", "Magick", "Magick Lore",
         "Incantation Magic", "Incantation Example: Minor Heating", "Womp"]
GM = ["Advice to the GM", "GM's Screen", "The First Adventure", "Campaign tracker",
      "Compacting information", "Conversion from other RPGs", "Other Resources"]
LITE = ["Amar Lite", "The first Amar Lite adventure"]
ADDONS = ["Universal Amar", "Experimental Systems", "Evolutionary Magick", "Electrify Path",
          "Elemental Path", "Healing Path", "Light Path", "Water Path"]
EVM = sorted(t for t in TITLES if t.endswith("(EVM)"))
SKIP = {"Magick", "Legacy Magick", "Raven Demon"}
LISTS = cat("Skills") + [t for t in cat("Spells") if t not in SKIP] + cat("Rituals") \
    + cat("Potions") + cat("Natural Magick Items")
WORLD = ["Mythology", "The World", "The Kingdom of Amar", "The Rise to Infamy", "Encounters",
         "Antonio The Magician", "Arius", "The Forbidden Library"] \
    + [t for t in cat("Gods") + cat("Places") + cat("NPCs") + cat("Encounters") if t not in SKIP - {"Raven Demon"}]
SCOPE = list(dict.fromkeys(RULES + GM + LITE + ADDONS + EVM + LISTS + WORLD))


def fname(title):
    return title.replace(" ", "_")


def html_of(title):
    return (SRC / "html" / (title.replace("/", "_") + ".html")).read_text()


def redirect_target(title):
    m = re.search(r'class="redirectText"><li><a href="/index\.php/([^"#]+)', html_of(title))
    return urllib.parse.unquote(m.group(1)).replace("_", " ") if m else None


REDIRECTS = {t: redirect_target(t) for t in TITLES}
REDIRECTS = {t: r for t, r in REDIRECTS.items() if r in SCOPE}
USED_IMAGES = set()


def link_for(target, frag):
    """Wiki link target -> site href. Pages outside the pilot point at the wiki."""
    target = REDIRECTS.get(target, target)
    frag = "#" + frag if frag else ""
    if target in SCOPE:
        return fname(target) + ".html" + frag
    if target.startswith("Category:"):
        c = target[9:]
        if any(c in CATS.get(t, []) for t in SCOPE):
            return fname(c) + ".html" + frag
    return WIKI + urllib.parse.quote(fname(target)) + frag


def clean(title):
    soup = BeautifulSoup(html_of(title), "lxml")
    root = soup.find("div", class_="mw-parser-output") or soup.body
    for sel in ["div#toc", "span.mw-editsection", "div.magnify", "style", "script",
                "div.printfooter", "div.catlinks", "table.mw-stack"]:
        for e in root.select(sel):
            e.decompose()
    for a in root.select("a.new"):
        if a.get_text().startswith("Template:"):
            a.decompose()
        else:
            a.unwrap()
    for e in root.find_all(["div", "p"]):
        t = e.get_text(" ", strip=True)
        if t.startswith("For the legacy") or (t.startswith("Back:") and len(t) < 60):
            e.decompose()
    # the site holds only the 3-tier system: no pointers to the legacy pages
    for li in root.find_all("li"):
        a = li.find("a")
        if a and "/Legacy_" in a.get("href", ""):
            li.decompose()
    # info boxes: a box of pictures only becomes a figure; the first box with data
    # becomes front matter (its picture, a god's symbol, shows in the stat card);
    # any later data box stays a table
    stats, symbol = {}, None
    for box in root.select("table.infobox"):
        pairs = [tr.find_all(["th", "td"]) for tr in box.find_all("tr")]
        pairs = [(a.get_text(" ", strip=True), b.get_text(" ", strip=True)) for a, b in
                 (c for c in pairs if len(c) == 2)]
        imgs = box.find_all("img")
        if not pairs and imgs:
            fig = soup.new_tag("div"); fig["class"] = "thumb tright"
            for im in imgs:
                fig.append(im.extract())
            box.replace_with(fig)
        elif not stats and pairs:
            stats = {k: v for k, v in pairs if k and v}
            if imgs:
                src = imgs[0].get("src", "")
                name = urllib.parse.unquote(src.split("/")[-1])
                if "/thumb/" in src:
                    name = re.sub(r"^\d+px-", "", name)
                if (WIKI_IMG / name).exists():
                    symbol = name
                    USED_IMAGES.add(name)
            box.decompose()
        else:
            box["class"] = "wikitable"
    # layout tables holding side-by-side tables -> the inner tables, stacked
    for outer in [t for t in root.find_all("table") if t.find("table")
                  and "wikitable" not in t.get("class", [])]:
        for x in [x for x in outer.find_all("table") if x.find_parent("table") is outer]:
            outer.insert_before(x)
        outer.decompose()
    # images: thumbs -> <figure>, everything -> images/<name>
    for img in root.find_all("img"):
        src = img.get("src", "")
        name = urllib.parse.unquote(src.split("/")[-1])
        if "/thumb/" in src:
            name = re.sub(r"^\d+px-", "", name)
        if not (WIKI_IMG / name).exists():
            img.decompose()
            continue
        USED_IMAGES.add(name)
        width = img.get("width")
        img.attrs = {"src": "images/" + name, "alt": img.get("alt", "") or ""}
        if width:
            img["width"] = width
        a = img.parent
        if a and a.name == "a" and "/File:" in a.get("href", ""):
            a.unwrap()
    for th in root.select("div.thumb"):
        img = th.find("img")
        if not img:
            th.decompose()
            continue
        cap = th.select_one("div.thumbcaption")
        side = "left" if "tleft" in th.get("class", []) else "center" if "tnone" in th.get("class", []) else "right"
        fig = soup.new_tag("figure")
        fig["class"] = side
        fig.append(img.extract())
        if cap and cap.get_text(strip=True):
            fc = soup.new_tag("figcaption")
            fc.string = cap.get_text(" ", strip=True)
            fig.append(fc)
        th.replace_with(fig)
    # links
    for a in root.find_all("a"):
        href = a.get("href", "")
        m = re.match(r"^(?:https?://(?:www\.)?d6gaming\.org)?/index\.php/([^#?]+)(?:#(.*))?", href)
        if m:
            a.attrs = {"href": link_for(urllib.parse.unquote(m.group(1)).replace("_", " "), m.group(2))}
        elif href.startswith("/"):
            a.attrs = {"href": "https://d6gaming.org" + href}
        elif href.startswith("#"):
            a.attrs = {"href": href}
        else:
            a.attrs = {"href": href}
    # headings: plain text; the page title is the h1, so drop a first heading repeating it
    for h in root.find_all(re.compile(r"^h[1-6]$")):
        h.string = h.get_text(" ", strip=True)
        h.attrs = {}
    first = root.find(re.compile(r"^h[1-6]$"))
    if first and first.get_text(strip=True).lower().startswith(title.lower()) \
            and not first.find_previous(["p", "table", "ul"]):
        first.decompose()
    # tables: bold first row -> header row; caption -> bold line above; no styling
    for t in root.find_all("table"):
        rows = t.find_all("tr")
        # a full-width first row is a title, a full-width last row a footnote
        ncols = max((sum(int(c.get("colspan", 1)) for c in r.find_all(["th", "td"])) for r in rows), default=0)
        def full(r):
            c = r.find_all(["th", "td"])
            return len(c) == 1 and int(c[0].get("colspan", 1)) == ncols > 1
        while len(rows) > 2 and full(rows[-1]):
            p = soup.new_tag("p")
            em = soup.new_tag("em")
            em.string = rows[-1].get_text(" ", strip=True)
            p.append(em)
            t.insert_after(p)
            rows.pop().decompose()
        if len(rows) > 2 and full(rows[0]) and not t.find("caption"):
            cap = soup.new_tag("caption")
            cap.string = rows[0].get_text(" ", strip=True)
            t.insert(0, cap)
            rows.pop(0).decompose()
        if rows and not rows[0].find("th"):
            tds = rows[0].find_all("td")
            if tds and all(td.get_text(strip=True) == (td.find("b").get_text(strip=True) if td.find("b") else None)
                           for td in tds if td.get_text(strip=True)):
                for td in tds:
                    td.name = "th"
                    if td.find("b"):
                        td.find("b").unwrap()
        # pandoc only sees a header row inside <thead>; MediaWiki puts it in <tbody>
        if rows and not t.find("thead") and rows[0].find_all("th") \
                and not rows[0].find("td"):
            head = soup.new_tag("thead")
            head.append(rows[0].extract())
            t.insert(0, head)
        cap = t.find("caption")
        if cap:
            text = cap.get_text(" ", strip=True)
            cap.decompose()
            if text and text.lower() != title.lower():
                p = soup.new_tag("p")
                b = soup.new_tag("strong")
                b.string = text
                p.append(b)
                t.insert_before(p)
    for e in root.find_all(True):
        for k in ("style", "class", "id", "border", "cellpadding", "cellspacing", "align", "valign",
                  "bgcolor", "scope", "title", "lang", "rel", "data-cls"):
            if k in e.attrs and not (e.name == "figure" and k == "class"):
                del e[k]
    # definition lists: a term with one meaning -> "**term**: meaning" bullet, a term with
    # several -> bullet with a sub-list, a lone term (the wiki's ";" heading) -> bold line
    for dl in root.find_all("dl")[::-1]:
        groups, cur = [], None
        for c in dl.find_all(["dt", "dd"], recursive=False):
            if c.name == "dt":
                cur = [c, []]; groups.append(cur)
            elif cur:
                cur[1].append(c)
            else:
                groups.append([None, [c]])
        out, ul = [], None
        for dt, dds in groups:
            if dt is None or not dds:
                p = soup.new_tag("p")
                if dt is None:
                    for x in list(dds[0].contents): p.append(x.extract())
                else:
                    b = soup.new_tag("strong"); b.string = dt.get_text(" ", strip=True); p.append(b)
                out.append(p); ul = None
                continue
            if ul is None:
                ul = soup.new_tag("ul"); ul["data-dl"] = "1"; out.append(ul)
            li = soup.new_tag("li"); b = soup.new_tag("strong"); b.string = dt.get_text(" ", strip=True)
            li.append(b)
            if len(dds) == 1:
                li.append(": ")
                for x in list(dds[0].contents): li.append(x.extract())
            else:
                sub = soup.new_tag("ul")
                for dd in dds:
                    sli = soup.new_tag("li")
                    for x in list(dd.contents): sli.append(x.extract())
                    sub.append(sli)
                li.append(sub)
            ul.append(li)
        for x in out:
            dl.insert_before(x)
        dl.decompose()
    # neighbouring lists made from separate wiki term lists become one list
    for ul in root.select('ul[data-dl]'):
        nxt = ul.find_next_sibling()
        while nxt is not None and nxt.name == "ul" and nxt.get("data-dl"):
            for li in nxt.find_all("li", recursive=False): ul.append(li.extract())
            gone, nxt = nxt, nxt.find_next_sibling()
            gone.decompose()
    for ul in root.select('ul[data-dl]'):
        del ul["data-dl"]
    for p in root.find_all("p"):
        if not p.get_text(strip=True) and not p.find("img"):
            p.decompose()
    for s in root.find_all("span"):
        s.unwrap()
    return "".join(str(c) for c in root.contents), stats, symbol


def to_markdown(html):
    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm-raw_attribute", "--wrap=none"],
                        input=html, capture_output=True, text=True, check=True).stdout
    md = re.sub(r"<colgroup>.*?</colgroup>\n?", "", md, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def front(meta):
    return "---\n" + yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000) + "---\n\n"


def main():
    only = sys.argv[1:]
    for title in (only or SCOPE):
        body, stats, symbol = clean(title)
        meta = {"title": title}
        cats = [c for c in CATS.get(title, []) if c not in ("Pages with broken file links",)]
        if cats:
            meta["categories"] = cats
        if symbol:
            meta["symbol"] = "images/" + symbol
        if stats:
            meta["stats"] = stats
        (PAGES / (fname(title) + ".md")).write_text(front(meta) + to_markdown(body))
    for t, r in REDIRECTS.items():
        if not only or r in only:
            (PAGES / (fname(t) + ".md")).write_text(front({"title": t, "redirect": r}))
    # web copies of the images: at most 1600 px wide
    for name in sorted(USED_IMAGES):
        out = IMAGES / name
        if out.exists():
            continue
        im = Image.open(WIKI_IMG / name)
        if im.width > 1600:
            im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
        if name.lower().endswith((".jpg", ".jpeg")):
            im.convert("RGB").save(out, quality=82, optimize=True, progressive=True)
        else:
            im.save(out, optimize=True)
    print(f"{len(only or SCOPE)} pages, {len(REDIRECTS)} redirects, {len(USED_IMAGES)} images")


if __name__ == "__main__":
    main()
