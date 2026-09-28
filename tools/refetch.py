#!/usr/bin/env python3
"""Refresh single pages of the wiki cache (~/Main/G/AMAR/Book/src/html).

Usage: tools/refetch.py "Title" ["Title" ...]
One request every half second, far below the server's flood limit of 300 a minute.
"""
import json, pathlib, sys, time, urllib.parse, urllib.request

CACHE = pathlib.Path.home() / "Main/G/AMAR/Book/src/html"
API = "https://d6gaming.org/api.php?action=parse&prop=text&formatversion=2&format=json&page="

for title in sys.argv[1:]:
    with urllib.request.urlopen(API + urllib.parse.quote(title.replace(" ", "_")), timeout=30) as r:
        text = json.load(r)["parse"]["text"]
    (CACHE / (title.replace("/", "_") + ".html")).write_text(text)
    print("fetched", title)
    time.sleep(0.5)
