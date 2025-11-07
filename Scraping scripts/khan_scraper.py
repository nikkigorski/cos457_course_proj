#!/usr/bin/env python3
import argparse, json, time, os, subprocess
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Load ignore links from JSON file (optional). If the file is missing or invalid,
# IGNORE_LINKS will be empty and no links will be filtered.
IGNORE_FILE = os.path.join(os.path.dirname(__file__), 'ignore_links.json')
try:
    with open(IGNORE_FILE, 'r', encoding='utf-8') as _f:
        _ignore_data = json.load(_f)
        IGNORE_LINKS = set(_ignore_data.get('links', []))
except Exception:
    IGNORE_LINKS = set()

def extract_meta_video(soup):
    urls = []
    for meta in soup.find_all('meta'):
        prop = meta.get('property') or meta.get('name') or ''
        if prop.lower() in ('og:video','og:video:url','og:video:secure_url') and meta.get('content'):
            urls.append(meta['content'])
    for v in soup.find_all('video'):
        for s in v.find_all('source'):
            if s.get('src'): urls.append(s['src'])
        if v.get('src'): urls.append(v['src'])
    return list(dict.fromkeys(urls))

def combine_url(base, href):
    from urllib.parse import urljoin
    return urljoin(base, href)

def extract_links(soup, base_url):
    ex = []
    others = []
    vids = []
    for a in soup.find_all('a', href=True):
        h = a['href']
        if h.startswith('/'):
                h = combine_url(base_url, h)
        if '/e/' in h:
            ex.append(h)
        elif '/v/' in h:
            vids.append(h)
        else:
            others.append(h)
    # remove duplicates while preserving order
    def _uniq(lst):
        return list(dict.fromkeys(lst))

    ex = _uniq(ex)
    others = _uniq(others)
    vids = _uniq(vids)

    # filter out any links that appear in the IGNORE_LINKS set
    if 'IGNORE_LINKS' in globals() and IGNORE_LINKS:
        ex = [u for u in ex if u not in IGNORE_LINKS]
        others = [u for u in others if u not in IGNORE_LINKS]
        vids = [u for u in vids if u not in IGNORE_LINKS]

    return {
        'exercises': ex,
        'links': others,
        'videos_from_links': vids,
    }

def parse_page(url, html):
    soup = BeautifulSoup(html,'html.parser')
    out={'url':url}
    out['title']=soup.title.string.strip() if soup.title and soup.title.string else None
    md=soup.find('meta', attrs={'name':'description'})
    out['description']=md['content'].strip() if md and md.get('content') else None
    v = extract_meta_video(soup)
    links_info = extract_links(soup, url)
    vids = []
    if v:
        vids.extend(v)
    vids.extend(links_info.get('videos_from_links', []))
    if vids:
        seen = set(); merged = []
        for u in vids:
            if u not in seen:
                merged.append(u); seen.add(u)
        out['videos'] = merged
    out['exercises'] = links_info.get('exercises', [])
    out['links'] = links_info.get('links', [])
    return out

def write_json(data, outpath):
    with open(outpath,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)


def start_driver():
    opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=opts)

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('url'); p.add_argument('name', nargs='?'); return p.parse_args()

def main():
    args=parse_args(); url=args.url; outpath=args.name if args.name else 'output.json'
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    d = start_driver(); d.get(url); time.sleep(1); html = d.page_source; d.quit()
    data = parse_page(url, html)
    write_json(data, outpath)
    
    video_urls = data.get('videos', [])
    if video_urls:
        out_dir = os.path.join(os.path.dirname(outpath) or '.', 'downloaded_videos')
        os.makedirs(out_dir, exist_ok=True)
        for vurl in video_urls:
            driver = start_driver()
            driver.get(vurl)
            time.sleep(1)
            page_html = driver.page_source
            driver.quit()
            soup = BeautifulSoup(page_html, 'html.parser')
            embeds = [iframe.get('src') for iframe in soup.find_all('iframe', src=True)
                      if 'youtube-nocookie.com/embed/' in iframe.get('src') or 'youtube.com/embed/' in iframe.get('src')]
            seen_embeds = set()
            unique_embeds = []
            for src in embeds:
                vid = src.split('/embed/')[-1].split('?')[0]
                if vid not in seen_embeds:
                    seen_embeds.add(vid)    
                    unique_embeds.append(src)
            for embed_src in unique_embeds[:2]:##only 2 for testing
                print(f"Found YouTube embed: {embed_src} on page {vurl}")
                cmd = [
                    'yt-dlp',
                    '--no-overwrites',
                    '-f', 'bestvideo+bestaudio/best',
                    '--merge-output-format', 'mkv',
                    embed_src,
                    '-o', os.path.join(out_dir, '%(title)s.%(ext)s'),
                ]
                subprocess.run(cmd)

if __name__=='__main__': main()
