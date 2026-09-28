#!/usr/bin/env python3
"""Illustrations for site pages with Gemini (Nano Banana Pro).

Usage: tools/gen_images.py npc "King Gorm" ...   |   creature "Troll" ...   |   scene "Equipment" ...
       tools/gen_images.py --all               (every job in JOBS below)

Each picture is drawn from the page itself: an NPC from its character sheet
(race, sex, age, height, weight, weapons, armour, equipment), a creature from its
description. A few pictures already on the site serve as the style to follow.
The full-size original goes to ~/Main/G/AMAR/Book/img/generated/ (for the book),
a web copy of at most 1600 px to site/images/<Page_Name>.jpg. Pictures that
exist are skipped, so a run can be repeated after a failure.
"""
import base64, concurrent.futures, io, json, pathlib, re, sys, time, urllib.request
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES, WEB = ROOT / "pages", ROOT / "site/images"
ORIG = pathlib.Path.home() / "Main/G/AMAR/Book/img/generated"
KEY = pathlib.Path("/home/.safe/gemini.txt").read_text().strip()
MODEL = "gemini-3-pro-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

REFS = {  # pictures on the site whose look the new ones follow
    "npc": ["King_Caolain_II.jpg", "Altira.jpg", "LorAigilos.jpg"],
    "creature": ["Treant.jpg", "Dungeon_creature.jpg", "Faerie_forest.jpg"],
    "scene": ["Anashina.jpg", "Faerie_forest.jpg", "King_Caolain_II.jpg"],
}
STYLE = ("Match the art style of the reference images: a painted digital fantasy illustration with realistic "
         "proportions, rich but natural colour, soft dramatic light and fine detail. Amar is a realistic, "
         "low-magic medieval fantasy world with a Nordic and European feel. No text, no letters, no captions, "
         "no frame, no border, no watermark, no signature.")
PROMPT = {
    "npc": ("Paint a portrait of {title}, a character in the Amar role-playing game. Show a three-quarter or "
            "full figure in a pose that fits the character, with a background that suits their home and role. "
            "Follow the character page below exactly: race, sex, age, height, weight and build, and show the "
            "weapons, armour, clothing and gear it lists. {style}\n\nCharacter page:\n{page}"),
    "creature": ("Paint the creature called {title} from the Amar role-playing game, whole and clearly seen, "
                 "in its natural surroundings, so a game master can show players what they meet. Follow the "
                 "description below: size, shape, colour and nature. {style}\n\nCreature page:\n{page}"),
    "scene": ("Paint an illustration for the page \"{title}\" of the Amar role-playing game, showing the "
              "scene, person or idea the page is about, so a reader sees it at a glance. {style}\n\nPage:\n{page}"),
}
ASPECT = {"npc": "3:4", "creature": "4:3", "scene": "4:3"}
UPRIGHT = {"Dwarf", "Elf", "Human", "Lizard Man", "Trollkin", "Merfolk", "Giant", "Troll", "Werewolf",
           "Faerie", "Centaur", "Half Elf", "Antonio The Magician", "Arax", "Ogre"}

JOBS = [("npc", t) for t in [
    "Alac Geoffryn", "Ayah", "Baron Fer Chalun", "Baron Garos Maella", "Baronesse Fienna Milin", "Boran",
    "Commander Seillan Torthal", "Eris", "Ferro", "High Priest Larosmarot", "Hina", "Kator", "King Gorm", "Kiro",
    "Lady Serena Chiall", "Lagioracharan", "Lord Nalchir Emaron", "Lord Thainir Laidhos", "Manir", "Mizamir",
    "Moltar the Just", "Naraghin", "Orach", "Povi", "Prince Vaiangor", "Princess Ianira", "Queen Fiona",
    "Ran-Asar", "Raven Demon", "The Rai", "Vinar", "Wayanah", "Yaloosi"]] + \
    [("creature", t) for t in [
    "Arax", "Brown Bear", "Cave Lion", "Centaur", "Deer", "Dragon", "Drake", "Dwarf", "Elf", "Faerie", "Giant",
    "Giant spider", "Griffin", "Horse", "Human", "King Eagle", "Lizard Man", "Merfolk", "Moose", "Mule",
    "Peregrine Falcon", "Pig", "Ram", "Rock-croc", "Sparrow Hawk", "Spell Searcher", "Troll", "Trollkin",
    "Two-headed badger", "Werewolf", "White Shark", "Wild Boar", "Wolf", "Wyvern"]] + \
    [("npc", "Antonio The Magician"), ("npc", "Half Elf")] + \
    [("scene", t) for t in ["The Forbidden Library", "Magick", "Incantation Magic", "Evolutionary Magick",
                            "Equipment", "Amar rules 101", "Advice to the GM", "Universal Amar"]]

EXTRA = {  # notes for pages where the first picture missed something
    "Two-headed badger": "It must have TWO separate heads on two necks, side by side, and SIX short legs, "
                         "three on each side of its long low body.",
    "Naraghin": "Absolutely no writing anywhere: no signs, labels or lettering on anything.",
    "Faerie": "Faeries are many races from the Otherworld: pixies, brownies, leprechauns, forest spirits, "
              "kelpies and water spirits. Show several different faeries together at play in a western forest, "
              "curious and mischievous, neither good nor evil.",
}

KEEP = re.compile(r"(character sheet|weapon|armou?r|equipment|gear|description|appearance|background|"
                  r"personality|history|clothing|combat|diet|habitat|social|special|mental)", re.I)


def page_text(title):
    """The parts of a page that say what to draw: the opening, the sheet, gear and descriptions."""
    body = (PAGES / (title.replace(" ", "_") + ".md")).read_text().split("---\n", 2)[2]
    body = re.sub(r"<figure.*?</figure>|<img[^>]*>", "", body, flags=re.S)
    parts = re.split(r"(?m)^(#{2,4} .*)$", body)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        if KEEP.search(parts[i]):
            out.append(parts[i] + parts[i + 1])
    return re.sub(r"\n{3,}", "\n\n", "".join(out)).strip()[:6000]


def ref_part(name):
    im = Image.open(WEB / name).convert("RGB")
    im.thumbnail((768, 768))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=85)
    return {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}


def generate(kind, title):
    stem = title.replace(" ", "_")
    web = WEB / f"{stem}.jpg"
    if web.exists():
        return title, "exists"
    prompt = PROMPT[kind].format(title=title, style=STYLE, page=page_text(title))
    if title in EXTRA:
        prompt = EXTRA[title] + "\n\n" + prompt
    aspect = "3:4" if kind == "npc" or title in UPRIGHT else ASPECT[kind]
    body = {"contents": [{"parts": [ref_part(r) for r in REFS[kind]] + [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"],
                                 "imageConfig": {"aspectRatio": aspect, "imageSize": "2K"}}}
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body).encode(), method="POST",
                                         headers={"Content-Type": "application/json", "x-goog-api-key": KEY})
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.load(r)
            parts = d["candidates"][0]["content"]["parts"]
            data = next(p["inlineData"]["data"] for p in parts if "inlineData" in p)
            break
        except Exception as e:
            err = e
            time.sleep(10 * (attempt + 1))
    else:
        return title, f"failed: {err}"
    raw = base64.b64decode(data)
    ORIG.mkdir(parents=True, exist_ok=True)
    im = Image.open(io.BytesIO(raw))
    im.save(ORIG / f"{stem}.png")
    im = im.convert("RGB")
    if max(im.size) > 1600:
        im.thumbnail((1600, 1600), Image.LANCZOS)
    im.save(web, "JPEG", quality=82, optimize=True, progressive=True)
    return title, f"ok {im.size[0]}x{im.size[1]}"


def main():
    args = sys.argv[1:]
    jobs = JOBS if args == ["--all"] else [(args[0], t) for t in args[1:]]
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        for title, result in pool.map(lambda j: generate(*j), jobs):
            print(f"{title}: {result}", flush=True)


if __name__ == "__main__":
    main()
