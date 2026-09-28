#!/usr/bin/env python3
"""Build the Amar RPG site.

  pages/*.md       one page each: YAML front matter (title, categories, stats) + Markdown
  nav.yaml         the menu
  template.html    the page frame
  site/            what the web server serves; this script writes site/*.html
                   and site/search.json, the images and theme/ are kept by hand

Run: python3 build.py
"""
import collections, html, json, pathlib, re, urllib.parse
import yaml
from markdown_it import MarkdownIt
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
PAGES, OUT = ROOT / "pages", ROOT / "site"
WIKI = "https://d6gaming.org/index.php/"
MD = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
NAV = yaml.load(open(ROOT / "nav.yaml"), Loader=yaml.BaseLoader)
TEMPLATE = (ROOT / "template.html").read_text()
esc = html.escape


# ──────────────────────────────────────────── pages
def load(f):
    text = f.read_text()
    meta, body = {}, text
    if text.startswith("---\n"):
        _, head, body = text.split("---\n", 2)
        meta = yaml.load(head, Loader=yaml.BaseLoader) or {}
    meta.setdefault("title", f.stem.replace("_", " "))
    meta.setdefault("categories", [])
    meta.setdefault("stats", {})
    meta["body"] = body
    return meta


PAGE = {p["title"]: p for p in map(load, sorted(PAGES.glob("*.md")))}


def fname(title):
    return "index.html" if title == "Main Page" else title.replace(" ", "_") + ".html"


def href(title, frag=""):
    return urllib.parse.quote(fname(title), safe="()'!,_-.~") + ("#" + frag if frag else "")


def members(cat):
    return sorted(t for t, p in PAGE.items() if cat in p["categories"])


CATEGORIES = sorted({c for p in PAGE.values() for c in p["categories"]})

# where a page sits when it is not in the menu itself
PARENT = {}
for t, p in PAGE.items():
    c = p["categories"]
    if "Skills" in c: PARENT[t] = "Skills"
    elif "Spells" in c: PARENT[t] = "Spells"
    elif "Rituals" in c: PARENT[t] = "Rituals"
    elif "Potions" in c: PARENT[t] = "Potions"
    elif "Natural Magick Items" in c: PARENT[t] = "Natural Magick Items"
    elif "Gods" in c: PARENT[t] = "Gods"
    elif "Places" in c: PARENT[t] = "Places"
    elif "NPCs" in c: PARENT[t] = "NPCs"
    elif "Encounters" in c: PARENT[t] = "Encounters"
    elif t.endswith("(EVM)") or t.endswith(" Path"): PARENT[t] = "Evolutionary Magick"
    elif t.endswith("(Playable Race)") or t == "Half Elf": PARENT[t] = "Playable Races"
PARENT.update({"Incantation Example: Minor Heating": "Incantation Magic", "Magick Lore": "Magick",
               "Antonio The Magician": "NPCs", "Arius": "NPCs", "The Forbidden Library": "Places"})
for c in CATEGORIES:
    if c.endswith(" Magick") or c in ("Advanced Spells", "Forbidden Spells"):
        PARENT.setdefault(c, "Spells")
    elif c.endswith(" Skills"):
        PARENT.setdefault(c, "Skills")

SECTION = {}
for s in NAV:
    for t in s["pages"]:
        SECTION[t] = s["section"]


def section_of(t):
    seen = set()
    while t not in SECTION and t in PARENT and t not in seen:
        seen.add(t)
        t = PARENT[t]
    return SECTION.get(t, ""), t


# ──────────────────────────────────────────── markdown -> html
IMG_SIZE = {}


def img_size(src):
    if src not in IMG_SIZE:
        try:
            im = Image.open(OUT / urllib.parse.unquote(html.unescape(src))).convert("RGB")
            w, h = im.size
            corners = [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]
            art = sum(min(im.getpixel(c)) > 215 for c in corners) >= 3
            IMG_SIZE[src] = (w, h, art)
        except Exception:
            IMG_SIZE[src] = None
    return IMG_SIZE[src]


def hid(text):
    return re.sub(r"\s+", "_", html.unescape(re.sub(r"<[^>]+>", "", text)).strip())


BROKEN = []


def polish(body, title):
    """Heading ids, table frames, captions, lazy images, link checks."""
    ids = set()

    def head(m):
        n, inner = m.group(1), m.group(2)
        i = base = hid(inner)
        k = 2
        while i in ids:
            i, k = f"{base}_{k}", k + 1
        ids.add(i)
        return f'<h{n} id="{esc(i, quote=True)}">{inner}</h{n}>'
    body = re.sub(r"<h([2-6])>(.*?)</h\1>", head, body, flags=re.S)
    body = re.sub(r"<p><strong>([^<]{1,80})</strong></p>\s*<table>", r'<table><caption>\1</caption>', body)
    body = re.sub(r"<thead>\s*<tr>(?:\s*<th>\s*</th>)+\s*</tr>\s*</thead>", "", body)

    def portrait(m):
        size = img_size(re.search(r'src="([^"]+)"', m.group(0)).group(1))
        return f'<figure class="right">{m.group(0)}</figure>' if size and size[1] > size[0] else m.group(0)
    # a tall picture standing alone (a portrait) sits beside the text
    body = re.sub(r"(?m)^<img\b[^>]*>$", portrait, body)
    body = body.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    # a footnote line right under a table belongs inside its frame
    body = re.sub(r'</table></div>\s*<p><em>([¹²³⁴⁵*†][^<]*)</em></p>', r'</table><p class="note">\1</p></div>', body)

    def img(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        size = img_size(src)
        extra = ' loading="lazy" decoding="async"'
        if size:
            w, h, art = size
            wm = re.search(r'width="(\d+)"', tag)
            dw = int(wm.group(1)) if wm else w
            if not wm:
                extra += f' width="{w}"'
            extra += f' height="{round(dw * h / w)}"'
            if art:
                extra += ' class="art"'
            tag = tag[:-2].rstrip() + extra + ">" if tag.endswith("/>") else tag[:-1] + extra + ">"
            # shrunk on the page: a tap opens the full picture, as on the wiki
            return f'<a class="full" href="{src}">{tag}</a>' if dw < w * 0.9 else tag
        return tag[:-2].rstrip() + extra + ">" if tag.endswith("/>") else tag[:-1] + extra + ">"
    body = re.sub(r"<img\b[^>]*>", img, body)

    def link(m):
        url = m.group(1)
        if url.startswith(WIKI):
            return f'<a class="wiki" title="On the old wiki" href="{url}"'
        if not re.match(r"^(https?:|mailto:|#)", url):
            target = urllib.parse.unquote(url.split("#")[0])
            if target and not (OUT / target).exists() and target[:-5].replace("_", " ") not in ALL_TITLES:
                BROKEN.append((title, url))
        return m.group(0)
    body = re.sub(r'<a href="([^"]*)"', link, body)
    # a drop cap opens the page when it starts with a real paragraph
    m = re.match(r"\s*<p>", body)
    if m and len(re.sub(r"<[^>]+>", "", body.split("</p>", 1)[0])) > 140:
        body = body.replace("<p>", '<p class="lede">', 1)
    return body


def text_of(body_html):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body_html))).strip()


def words(body_html):
    """The section's distinct words, most frequent first, so search can rank by position."""
    n = collections.Counter(re.findall(r"[a-z0-9][a-z0-9'’-]{1,}", text_of(body_html).lower()))
    return " ".join(sorted(n, key=lambda w: (-n[w], w)))


def summary(t):
    p = PAGE.get(t)
    if not p:
        return ""
    txt = text_of(MD.render(re.sub(r"^\s*(#.*|\|.*|<.*|\*\*[^*]+\*\*\s*)$", "", p["body"], flags=re.M)))
    s = re.split(r"(?<=[.!?])\s", txt, maxsplit=1)[0]
    return s if len(s) < 180 else s[:170].rsplit(" ", 1)[0] + " …"


# ──────────────────────────────────────────── generated lists
def link_list(titles):
    out = ['<ul class="index">']
    for t in titles:
        s, sym = summary(t), PAGE.get(t, {}).get("symbol")
        icon = f'<img class="symbol" src="{esc(sym, quote=True)}" alt="">' if sym else ""
        out.append(f'<li>{icon}<a href="{href(t)}">{esc(t)}</a>' + (f" <span>{esc(s)}</span>" if s else "") + "</li>")
    return "\n".join(out + ["</ul>"])


def stat_table(titles, cols, first):
    out = [f'<div class="tw"><table class="list"><thead><tr><th>{first}</th>'
           + "".join(f"<th>{esc(label)}</th>" for label, _ in cols) + "</tr></thead><tbody>"]
    for t in titles:
        st = PAGE[t]["stats"]
        mark = (" ◆" if "Advanced Spells" in PAGE[t]["categories"] else "") \
            + (" ★" if "Forbidden Spells" in PAGE[t]["categories"] else "")
        cells = []
        for _, keys in cols:
            v = next((st[k] for k in keys if st.get(k)), "")
            cells.append("<td>" + esc(v.replace(" Mental Fortitude", " MF").rstrip(".")) + "</td>")
        out.append(f'<tr><td><a href="{href(t)}">{esc(t)}</a>{mark}</td>' + "".join(cells) + "</tr>")
    return "\n".join(out + ["</tbody></table></div>"])


SPELL_COLS = [("DR", ["DR"]), ("Cost", ["Cost"]), ("Cast", ["Casting Time"]), ("Range", ["Distance", "Range"]),
              ("Duration", ["Duration"]), ("Area", ["Area of Effect"])]
RITUAL_COLS = [("DR", ["DR"]), ("Cast", ["Casting Time"]), ("Range", ["Range", "Distance"]),
               ("Duration", ["Duration"]), ("Area", ["Area of Effect"]), ("Resist", ["Resist?"])]
POTION_COLS = [("DR", ["DR"]), ("Lasts", ["Duration"]), ("Brewing", ["Production time"]),
               ("Keeps", ["Expiration"]), ("Price", ["Market price"])]
SPELL_KEY = '<p class="key">◆ advanced spell, ★ forbidden spell. MF is Mental Fortitude.</p>'


def domains():
    return [c for c in CATEGORIES if c.endswith(" Magick") and members(c)
            and any("Spells" in PAGE[t]["categories"] for t in members(c))]


def generated(title):
    """Body for a page that is a list, or '' when the page is written by hand only."""
    if title == "Skills":
        return "\n".join(f'<h2 id="{hid(c)}">{c}</h2>\n' + link_list(members(c))
                         for c in ("Physical Skills", "Mental Skills", "Perception Skills"))
    if title == "Spells":
        doms = domains()
        out = ['<p>Every spell is listed under each domain it belongs to. '
               'The casting roll is O6 + SPIRIT + Attunement + domain against the DR.</p>', SPELL_KEY,
               '<p class="jump">' + " ".join(f'<a href="#{hid(d)}">{esc(d.replace(" Magick", ""))}</a>' for d in doms) + "</p>"]
        for d in doms:
            out.append(f'<h2 id="{hid(d)}">{esc(d)}</h2>')
            out.append(stat_table([t for t in members(d) if "Spells" in PAGE[t]["categories"]], SPELL_COLS, "Spell"))
        return "\n".join(out)
    if title in domains() or title in ("Advanced Spells", "Forbidden Spells"):
        return SPELL_KEY + stat_table([t for t in members(title) if "Spells" in PAGE[t]["categories"]], SPELL_COLS, "Spell")
    if title == "Rituals":
        return stat_table(members("Rituals"), RITUAL_COLS, "Ritual")
    if title == "Potions":
        return stat_table(members("Potions"), POTION_COLS, "Potion")
    if title in CATEGORIES:
        rest = [t for t in members(title) if t != title]
        return link_list(rest) if rest else ""
    return ""


GENERATED_ONLY = ["Skills", "Spells", "Rituals", "Potions"] + [c for c in CATEGORIES if c not in PAGE]
ALL_TITLES = set(PAGE) | set(GENERATED_ONLY)


# ──────────────────────────────────────────── frame
def nav_html(current):
    sec, top = section_of(current)
    out = []
    for s in NAV:
        items = []
        for t in s["pages"]:
            cur = ' aria-current="page"' if t == current else ' class="here"' if t == top else ""
            items.append(f'<li><a href="{href(t)}"{cur}>{esc(t)}</a></li>')
        out.append(f'<h2>{esc(s["section"])}</h2><ul>' + "".join(items) + "</ul>")
    return "\n".join(out)


def stats_html(st, symbol=None):
    rows = [(k, v) for k, v in st.items() if v and v != "See below"]
    if not rows:
        return ""
    sym = f'<img class="symbol" src="{esc(symbol, quote=True)}" alt="">' if symbol else ""
    return f'<aside class="stats">{sym}<dl>' + "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows) + "</dl></aside>"


def toc_html(body):
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, flags=re.S)
    if len(heads) < 4:
        return ""
    # open on a wide screen, folded on a phone; the inline script runs before the first paint
    return ('<details class="toc" open><summary>On this page</summary><ol>' + "".join(
        f'<li><a href="#{i}">{t}</a></li>' for i, t in heads) + "</ol></details>"
        '<script>if (innerWidth < 840) document.currentScript.previousElementSibling.open = false</script>')


def crumbs(title):
    sec, _ = section_of(title)
    parent = PARENT.get(title)
    bits = [esc(sec)] if sec else []
    if parent and parent != title:
        bits.append(f'<a href="{href(parent)}">{esc(parent)}</a>')
    return f'<p class="crumbs">{" / ".join(bits)}</p>' if bits else ""


def page(title, body, desc="", cls="", head_extra=""):
    doc = TEMPLATE
    for k, v in {"title": esc(title if title == "Amar RPG" else f"{title} – Amar RPG"),
                 "desc": esc(desc, quote=True), "cls": cls, "nav": nav_html(title),
                 "content": body, "head": head_extra}.items():
        doc = doc.replace("{" + k + "}", v)
    return doc


def main():
    written, index = set(), []
    for t in sorted(ALL_TITLES):
        p = PAGE.get(t, {"title": t, "categories": [], "stats": {}, "body": ""})
        if p.get("redirect"):
            to = href(p["redirect"])
            doc = (f'<!doctype html><meta charset="utf-8"><title>{esc(t)}</title>'
                   f'<meta http-equiv="refresh" content="0; url={to}"><link rel="canonical" href="{to}">'
                   f'<p>This page moved to <a href="{to}">{esc(p["redirect"])}</a>.</p>')
            (OUT / fname(t)).write_text(doc)
            written.add(fname(t))
            continue
        own = polish(MD.render(p["body"]), t)
        body = own + generated(t)
        if t == "Main Page":
            content, desc, cls = body, "Amar, a realistic and simple role-playing game played with one six-sided die.", "home"
        else:
            cats = [c for c in p["categories"] if c != t]
            foot = ('<p class="cats">Listed under ' + ", ".join(
                f'<a href="{href(c)}">{esc(c)}</a>' for c in cats) + ".</p>") if cats else ""
            content = crumbs(t) + f"<h1>{esc(t)}</h1>" + stats_html(p["stats"], p.get("symbol")) + toc_html(own) \
                + f'<div class="text">{body}</div>' + foot
            desc, cls = summary(t), ""
        (OUT / fname(t)).write_text(page("Amar RPG" if t == "Main Page" else t, content, desc, cls))
        written.add(fname(t))
        if t != "Main Page":
            # one entry per page and per h2/h3 section; "w" holds the section's words
            sec, _ = section_of(t)
            parts = re.split(r'(<h[23] id="[^"]+">.*?</h[23]>)', body, flags=re.S)
            index.append({"t": t, "u": href(t), "s": sec, "w": words(parts[0] + stats_html(p["stats"]))})
            for k in range(1, len(parts), 2):
                i, h = re.match(r'<h[23] id="([^"]+)">(.*?)</h[23]>', parts[k], flags=re.S).groups()
                index.append({"t": text_of(h), "u": href(t, i), "s": t, "w": words(parts[k + 1])})
    (OUT / "search.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")))
    for f in OUT.glob("*.html"):
        if f.name not in written:
            f.unlink()
    print(f"{len(written)} pages, {len(index)} search entries")
    for t, u in BROKEN:
        print(f"broken link: {t} -> {u}")


if __name__ == "__main__":
    main()
