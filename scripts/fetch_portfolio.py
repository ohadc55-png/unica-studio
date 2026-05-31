# -*- coding: utf-8 -*-
"""Fetch Unica Studio portfolio images from the public Google Drive folder,
optimize them (resize + WebP/JPG), and emit a manifest for the site."""
import io
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(ROOT, "static", "img", "projects")
DATA_DIR = os.path.join(ROOT, "data")

API_KEY = "AIzaSyC1qbk75NzWBvSaDh6KnsjjA9pIrP4lYIE"
REFERER = "https://drive.google.com"

# Display order chosen for the portfolio. (title, slug, drive folder target id)
PROJECTS = [
    ("השלום 31", "hashalom-31", "1j0TlYFUg2me46mG0t8WIsnh-fXId44sc"),
    ("דוד המלך 25", "david-hamelech-25", "1DEnXM1c-EpiUXkD736qr01YLMSpeVYMP"),
    ("אברהם אבינו 33", "avraham-avinu-33", "1UzX0JK1XZCHKDqQ6Vn_lNZ5K8_A3Bt6S"),
    ("גיורא 24", "giora-24", "1VG8NkdJZCKiXrFg25sl3upSKawJcMBtf"),
    ("אברהם אבינו 24", "avraham-avinu-24", "1HFG-6FYsNW9JWmtJMDcqFxsIuYJbRsOi"),
    ("מטודלה 6", "matudela-6", "1RvxP-U4L0eFwi4fJyqT6mhydL_Z6oyKZ"),
    ("בר גיורא 18", "bar-giora-18", "1mPJGtapLKQmqiI42J3XSH-8H7n9Y7IT0"),
]

FULL_W = 1920
THUMB_W = 760
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "Mozilla/5.0", "Referer": REFERER})


def list_images(folder_id):
    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": f"'{folder_id}' in parents and mimeType contains 'image/'",
        "key": API_KEY,
        "fields": "files(id,name,mimeType,imageMediaMetadata(width,height))",
        "pageSize": 300,
        "orderBy": "name_natural",
    }
    r = SESSION.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("files", [])


def download_bytes(file_id):
    # The thumbnail endpoint returns a server-scaled JPEG without needing auth.
    url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w2400"
    r = SESSION.get(url, timeout=60)
    r.raise_for_status()
    return r.content


def save_variant(img, path_base, width, quality):
    w, h = img.size
    if w > width:
        nh = round(h * width / w)
        im = img.resize((width, nh), Image.LANCZOS)
    else:
        im = img.copy()
    im.save(path_base + ".webp", "WEBP", quality=quality, method=6)
    rgb = im.convert("RGB")
    rgb.save(path_base + ".jpg", "JPEG", quality=quality + 3, optimize=True, progressive=True)
    return im.size


def process_one(slug, idx, file_id):
    raw = download_bytes(file_id)
    img = Image.open(io.BytesIO(raw))
    img = ImageOps.exif_transpose(img)
    full_dir = os.path.join(IMG_DIR, slug, "full")
    thumb_dir = os.path.join(IMG_DIR, slug, "thumb")
    os.makedirs(full_dir, exist_ok=True)
    os.makedirs(thumb_dir, exist_ok=True)
    name = f"{idx:02d}"
    fw, fh = save_variant(img, os.path.join(full_dir, name), FULL_W, 82)
    save_variant(img, os.path.join(thumb_dir, name), THUMB_W, 78)
    return {
        "full": f"img/projects/{slug}/full/{name}.webp",
        "full_jpg": f"img/projects/{slug}/full/{name}.jpg",
        "thumb": f"img/projects/{slug}/thumb/{name}.webp",
        "thumb_jpg": f"img/projects/{slug}/thumb/{name}.jpg",
        "w": fw,
        "h": fh,
        "landscape": fw >= fh,
    }


def main():
    manifest = {"projects": []}
    for title, slug, folder_id in PROJECTS:
        files = list_images(folder_id)
        files.sort(key=lambda f: f["name"])
        print(f"[{slug}] {len(files)} images...", flush=True)
        images = [None] * len(files)
        with ThreadPoolExecutor(max_workers=8) as ex:
            futs = {
                ex.submit(process_one, slug, i + 1, f["id"]): i
                for i, f in enumerate(files)
            }
            done = 0
            for fut in as_completed(futs):
                i = futs[fut]
                try:
                    images[i] = fut.result()
                except Exception as e:  # noqa
                    print(f"   ! {slug} #{i+1} failed: {e}", flush=True)
                done += 1
                if done % 6 == 0 or done == len(files):
                    print(f"   {slug}: {done}/{len(files)}", flush=True)
        images = [im for im in images if im]
        cover = next((im for im in images if im["landscape"]), images[0]) if images else None
        manifest["projects"].append({
            "title": title,
            "slug": slug,
            "count": len(images),
            "cover": cover["full"] if cover else "",
            "cover_jpg": cover["full_jpg"] if cover else "",
            "images": images,
        })
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(os.path.join(DATA_DIR, "portfolio.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    total = sum(p["count"] for p in manifest["projects"])
    print(f"\nDONE: {len(manifest['projects'])} projects, {total} images.", flush=True)


if __name__ == "__main__":
    main()
