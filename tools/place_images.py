#!/usr/bin/env python3
"""Put a picture on its page: a right-floated figure after the opening paragraph,
or at the top when the page starts with a heading or a table.

Usage: tools/place_images.py "Page Title=Image.jpg" ...
       tools/place_images.py --generated     (every page whose picture gen_images.py made)
A page that already shows the picture is left alone.
"""
import pathlib, re, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES, WEB = ROOT / "pages", ROOT / "site/images"


def place(title, image):
    f = PAGES / (title.replace(" ", "_") + ".md")
    text = f.read_text()
    if f"images/{image}" in text:
        return "already there"
    w, h = Image.open(WEB / image).size
    width = 340 if h > w else 420
    fig = f'<figure class="right">\n<img src="images/{image}" width="{width}" alt="{title}" />\n</figure>\n\n'
    _, head, body = text.split("---\n", 2)
    lead = body.lstrip("\n")
    m = re.match(r"(?:[^#|<\n][^\n]*\n)+\n", lead)          # an opening paragraph
    body = lead[:m.end()] + fig + lead[m.end():] if m else fig + lead
    f.write_text("---\n" + head + "---\n\n" + body)
    return "placed"


def main():
    args = sys.argv[1:]
    if args == ["--generated"]:
        sys.path.insert(0, str(ROOT / "tools"))
        from gen_images import JOBS
        pairs = [(t, t.replace(" ", "_") + ".jpg") for _, t in JOBS if (WEB / (t.replace(" ", "_") + ".jpg")).exists()]
    else:
        pairs = [a.split("=", 1) for a in args]
    for t, img in pairs:
        print(f"{t}: {place(t, img)}")


if __name__ == "__main__":
    main()
