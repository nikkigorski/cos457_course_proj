#!/usr/bin/env python3

import argparse
import json
import os
import random
import datetime
import urllib.parse
import re


def _truncate_string(s, length):
    if s is None:
        return None
    s = str(s).strip()
    return s if len(s) <= length else s[:length]


def _extract_youtube_id(url):
    if not url:
        return None
    m = re.search(r'(?:embed/|v=|youtu\.be/)([A-Za-z0-9_-]{6,})', url)
    return m.group(1) if m else None


def normalize_youtube_url(url):
    vid = _extract_youtube_id(url)
    if vid:
        return f'https://www.youtube.com/watch?v={vid}'
    return url


def compute_image_size(entry):
    if not isinstance(entry, dict):
        return 1
    for key in ('Size', 'size'):
        if key in entry:
            try:
                v = int(entry[key])
                return v if v > 0 else 1
            except Exception:
                pass
    w = None; h = None
    for key in ('width', 'Width', 'W', 'w'):
        if key in entry and isinstance(entry[key], (int, float)):
            w = int(entry[key]); break
    for key in ('height', 'Height', 'H', 'h'):
        if key in entry and isinstance(entry[key], (int, float)):
            h = int(entry[key]); break
    try:
        if isinstance(w, int) and isinstance(h, int):
            return max(1, w * h)
        if isinstance(w, int):
            return max(1, w)
        if isinstance(h, int):
            return max(1, h)
    except Exception:
        pass
    return 1


def gen_id(existing):
    for _ in range(100000):
        c = random.randint(1, 2**31 - 1)
        if c not in existing:
            existing.add(c)
            return c
    raise RuntimeError('unable to generate unique id')


def canonical_keys(obj):
    mapping = {}
    for k in obj.keys():
        mapping[k.lower()] = k
    return mapping


def clean_data(data, preserve_ids=False):
    
    if not isinstance(data, dict):
        raise ValueError('expected top-level JSON object')

    # make sure canonical top-level arrays exist
    top = {}
    for name in ('Resource', 'Note', 'pdf', 'Image', 'Video', 'Website'):
        # accept lowercase versions
        found = data.get(name) or data.get(name.lower()) or []
        top[name] = list(found) if isinstance(found, list) else []

    # collect used resource ids
    used_ids = set()
    for r in top['Resource']:
        if isinstance(r, dict) and isinstance(r.get('ResourceID'), int):
            used_ids.add(r['ResourceID'])

    # build a mapping for existing Image rows (Link -> ResourceID)
    url_to_img_res = {}
    for img in top['Image']:
        if not isinstance(img, dict):
            continue
        link = img.get('Link') or img.get('link') or img.get('url')
        rid = img.get('ResourceID') if isinstance(img.get('ResourceID'), int) else None
        if link:
            if rid is not None:
                url_to_img_res[link] = rid


    # collect all image candidates from existing Image rows
    all_image_entries = []
    for img in top['Image']:
        if not isinstance(img, dict):
            continue
        link = img.get('Link') or img.get('link') or img.get('url')
        if not link:
            continue
        size_val = compute_image_size(img)
        alt = None
        # try to find alt in Note rows that reference this ResourceID
        alt = img.get('Alt') or img.get('alt') or img.get('Title') or img.get('title')
        all_image_entries.append({'url': link, 'alt': alt, 'size': size_val, 'orig': img})

    # dedupe by URL
    dedup = {}
    for it in all_image_entries:
        if not it.get('url'):
            continue
        if it['url'] in dedup:
            if dedup[it['url']].get('size', 0) < it.get('size', 0):
                dedup[it['url']] = it
        else:
            dedup[it['url']] = it

    # ensure each unique image URL has a Resource and Image row, and that Notes reference the same ResourceID
    new_resources = list(top['Resource'])
    new_images = []
    new_notes = list(top['Note'])

    for url, info in dedup.items():
        # reuse existing ResourceID if present
        rid = None
        if url in url_to_img_res:
            rid = url_to_img_res[url]
        if rid is None and preserve_ids:
            rid = None
        if rid is None:
            rid = gen_id(used_ids)
            # create a Resource entry for this image
            topic = _truncate_string(info.get('alt') or os.path.basename(urllib.parse.urlparse(url).path) or 'image', 25)
            new_resources.append({
                'ResourceID': rid,
                'Date': datetime.date.today().isoformat(),
                'DateFor': datetime.date.today().isoformat(),
                'Author': 'khan accademy, lobster notes web scraper',
                'Topic': topic,
                'Keywords': None,
                'Rating': 9.9,
                'Format': 'Image',
                'isVerified': False,
            })
        # create Image row
        size_val = int(info.get('size') or 1)
        if size_val <= 0:
            size_val = 1
        new_images.append({'ResourceID': rid, 'Link': url, 'Size': size_val})
        # attach a Note for the image 
        alt_text = info.get('alt')
        if alt_text:
            new_notes.append({'ResourceID': rid, 'Body': _truncate_string(alt_text, 2048)})

    # normalize videos    
    new_videos = []
    for v in top['Video']:
        if not isinstance(v, dict):
            continue
        link = v.get('Link') or v.get('link')
        if link:
            v['Link'] = normalize_youtube_url(link)
        new_videos.append(v)

    # normalize websites
    new_websites = []
    for w in top['Website']:
        if not isinstance(w, dict):
            continue
        link = w.get('Link') or w.get('link')
        if link:
            w['Link'] = link
        new_websites.append(w)

    # pdfs and notes
    new_pdfs = []
    for p in top['pdf']:
        if not isinstance(p, dict):
            continue
        body = p.get('Body') or p.get('body') or p.get('filepath') or p.get('url')
        url=body
        new_pdfs.append({'ResourceID': p.get('ResourceID'), 'Link': url, 'Body': _truncate_string(body, 2048)})

    # ensure Resource topics and note bodies truncated
    final_resources = []
    for r in new_resources:
        if not isinstance(r, dict):
            continue
        r['Topic'] = _truncate_string(r.get('Topic'), 25) or 'image'
        final_resources.append(r)

    # assemble result
    out = {
        'Resource': final_resources,
        'Note': new_notes,
        'pdf': new_pdfs,
        'Image': new_images,
        'Video': new_videos,
        'Website': new_websites,
    }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('output', nargs='?', help='output file (optional)')
    p.add_argument('--preserve-ids', action='store_true', help='try to reuse existing ResourceIDs when present')
    args = p.parse_args()

   
    if not args.output:
        inp = args.input
        idir, ifname = os.path.split(inp)
        name, ext = os.path.splitext(ifname)
        if not ext:
            ext = '.json'
        outp = os.path.join(idir or '.', f"{name}_cleaned{ext}")
    else:
        outp = args.output

    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned = clean_data(data, preserve_ids=args.preserve_ids)

    with open(outp, 'w', encoding='utf-8') as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f'Wrote cleaned data to {outp}')


if __name__ == '__main__':
    main()