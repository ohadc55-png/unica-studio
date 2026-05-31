# -*- coding: utf-8 -*-
"""One-off fixups after user clarification:
  - "גיורא 24" and "אברהם אבינו 24" are TWO different apartments (not a dup).
  - Re-download "אברהם אבינו 24"; rename giora-24's display title to "בר גיורא 24".
  - Pick distinct covers; add a curated hero slideshow list.
"""
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fetch_portfolio as fp  # reuse list_images / process_one / paths

ROOT = fp.ROOT
MAN = os.path.join(fp.DATA_DIR, "portfolio.json")

AA24_SLUG = "avraham-avinu-24"
AA24_FOLDER = "1HFG-6FYsNW9JWmtJMDcqFxsIuYJbRsOi"


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def download_project(slug, folder_id):
    files = fp.list_images(folder_id)
    files.sort(key=lambda f: f["name"])
    print(f"[{slug}] {len(files)} images...", flush=True)
    images = [None] * len(files)
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fp.process_one, slug, i + 1, f["id"]): i for i, f in enumerate(files)}
        for fut in as_completed(futs):
            i = futs[fut]
            images[i] = fut.result()
    return [im for im in images if im]


def main():
    man = json.load(open(MAN, encoding="utf-8"))
    projects = {p["slug"]: p for p in man["projects"]}

    # 1) rename giora-24 -> "בר גיורא 24"
    if "giora-24" in projects:
        projects["giora-24"]["title"] = "בר גיורא 24"

    # 2) re-download אברהם אבינו 24
    aa_imgs = download_project(AA24_SLUG, AA24_FOLDER)

    # distinct cover: prefer a landscape image unique to AA24 (not in giora-24)
    giora_hashes = set()
    g = projects.get("giora-24")
    if g:
        for im in g["images"]:
            p = os.path.join(ROOT, "static", im["full_jpg"].replace("/", os.sep))
            if os.path.exists(p):
                giora_hashes.add(md5(p))

    def is_unique_landscape(im):
        if not im["landscape"]:
            return False
        p = os.path.join(ROOT, "static", im["full_jpg"].replace("/", os.sep))
        return os.path.exists(p) and md5(p) not in giora_hashes

    cover = next((im for im in aa_imgs if is_unique_landscape(im)),
                 next((im for im in aa_imgs if im["landscape"]), aa_imgs[0]))

    aa_entry = {
        "title": "אברהם אבינו 24",
        "slug": AA24_SLUG,
        "count": len(aa_imgs),
        "cover": cover["full"],
        "cover_jpg": cover["full_jpg"],
        "images": aa_imgs,
    }

    # 3) rebuild ordered project list (keep the two overlapping apartments apart)
    order = ["matudela-6", AA24_SLUG, "avraham-avinu-33", "david-hamelech-25",
             "hashalom-31", "giora-24", "bar-giora-18"]
    projects[AA24_SLUG] = aa_entry
    man["projects"] = [projects[s] for s in order if s in projects]

    # 4) curated hero slideshow (warm, styled rooms across projects)
    hero_candidates = [
        ("matudela-6", 2), ("avraham-avinu-33", 24), ("giora-24", 5),
        ("david-hamelech-25", 17), ("matudela-6", 3),
    ]
    slides = []
    seen = set()
    for slug, idx in hero_candidates:
        p = projects.get(slug)
        if not p:
            continue
        imgs = p["images"]
        im = imgs[idx - 1] if 0 <= idx - 1 < len(imgs) and imgs[idx - 1]["landscape"] else \
            next((x for x in imgs if x["landscape"]), imgs[0])
        if im["full"] in seen:
            continue
        seen.add(im["full"])
        slides.append({"full": im["full"], "full_jpg": im["full_jpg"]})
    man["hero_slides"] = slides
    man["hero"] = {"full": slides[0]["full"], "full_jpg": slides[0]["full_jpg"]}

    json.dump(man, open(MAN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\nprojects:")
    for p in man["projects"]:
        print(f"  {p['slug']:18} {p['title']:14} {p['count']:>2} imgs")
    print("hero slides:", len(slides))
    for s in slides:
        print("   ", s["full"])


if __name__ == "__main__":
    main()
