#!/usr/bin/env python3
import argparse, json, time, os, subprocess
import urllib.request
import urllib.parse
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
import random

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


def _extract_youtube_id(url):
    if not url:
        return None
    m = re.search(r'(?:embed/|v=|youtu\.be/)([A-Za-z0-9_-]{6,})', url)
    if m:
        return m.group(1)
    return None


def _normalize_youtube_url(url):
    vid = _extract_youtube_id(url)
    if vid:
        return f'https://www.youtube.com/watch?v={vid}'
    return url




def download_pdf(url, target_dir, documents):
    print(f"Attempting to download PDF from: {url}")
    try:                                                           #try to catch timeout or invalid URL
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=15) as resp:
            final = resp.geturl()
        base = os.path.basename(urllib.parse.urlparse(final).path)
        base = urllib.parse.unquote(base) if base else base
        name = base or 'document'
        name = name.replace('%', ' ').replace('_', ' ').strip()
        if not name:
            name = 'document'
        if not name.lower().endswith('.pdf'):
            name = f"{name}.pdf"
        target_path = os.path.join(target_dir, name)
        urllib.request.urlretrieve(final, target_path)
        with open(target_path, 'rb') as fh:
            head = fh.read(1024)
        try:
            head_text = head.decode('utf-8', errors='ignore').lstrip().lower()
        except Exception:
            head_text = ''
        if head_text.startswith('<!doctype html'):
            os.remove(target_path)
            return False
        documents.append({'title': name, 'filepath': os.path.abspath(target_path), 'url': final})
        return True
    except (urllib.error.URLError, TimeoutError, Exception) as e: #except condition for timeout or URL 
            print(f"Error: Download failed from {url}, {e}") 
            return False

def extract_links(soup, base_url):
    ex = []
    others = []
    vids = []
    for a in soup.find_all('a', href=True):
        h = a['href']
        if h.startswith('/'):
                h = combine_url(base_url, h)
        lower_h = h.lower()
        # Treat any link containing '/e/' or the keywords quiz/test/activity as an exercise
        if ('/e/' in lower_h) or any(k in lower_h for k in ('quiz', 'test', 'activity')):
            ex.append(h)
        elif '/v/' in lower_h:
            vids.append(h)
        else:
            others.append(h)
    def _uniq(lst):
        return list(dict.fromkeys(lst))

    ex = _uniq(ex)
    others = _uniq(others)
    vids = _uniq(vids)

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

def _truncate_string(s, length):
    if s is None:
        return None
    s = str(s).strip()
    return s if len(s) <= length else s[:length]

def write_json(data, outpath):
    today = datetime.date.today().isoformat()
    resources = []
    notes = []
    pdfs = []
    images = []
    videos = []
    websites = []

    # collect used ids from existing file to avoid collisions across runs
    used_ids = set()
    if os.path.exists(outpath):
        try:
            with open(outpath, 'r', encoding='utf-8') as ef:
                existing = json.load(ef)
            if isinstance(existing, dict):
                for tab in ('Resource', 'Note', 'pdf', 'Image', 'Video', 'Website'):
                    for row in existing.get(tab, []) if isinstance(existing.get(tab, []), list) else []:
                        rid = row.get('ResourceID') if isinstance(row, dict) else None
                        if isinstance(rid, int):
                            used_ids.add(rid)
        except Exception:
            used_ids = set()

    def gen_id():
        # 32-bit unsigned-ish range, avoid 0
        for _ in range(10000):
            candidate = random.randint(1, 2**31-1)
            if candidate not in used_ids:
                used_ids.add(candidate)
                return candidate
        raise RuntimeError('unable to generate unique ResourceID')

    page_title = data.get('title') if isinstance(data, dict) else None
    page_desc = data.get('description') if isinstance(data, dict) else None
    page_url = data.get('url') if isinstance(data, dict) else None

    # Page resource
    page_id = gen_id()
    resources.append({
        'ResourceID': page_id,
        'Date': today,
        'DateFor': today,
        'Author': 'khan accademy, lobster notes web scraper',
        'Topic': _truncate_string(page_title, 25),
        'Keywords': None,
        'Rating': 9.9,
        'Format': 'Website',
        'isVerified': False,
    })
    if page_url and re.match(r'^https?://', str(page_url)):
        websites.append({'ResourceID': page_id, 'Link': page_url})
    if page_desc:
        notes.append({'ResourceID': page_id, 'Body': _truncate_string(page_desc, 2048)})

    # Videos
    for v in (data.get('videoData') if isinstance(data, dict) else []) or []:
        vid_id = gen_id()
        title = v.get('title') if isinstance(v, dict) else None
        filepath = v.get('filepath') if isinstance(v, dict) else None
        duration = v.get('duration') if isinstance(v, dict) else None
        link = v.get('link') if isinstance(v, dict) else None
        resources.append({
            'ResourceID': vid_id,
            'Date': today,
            'DateFor': today,
            'Author': 'khan accademy, lobster notes web scraper',
            'Topic': _truncate_string(title, 25),
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Video',
            'isVerified': False,
        })
        dur = int(duration) if isinstance(duration, (int, float)) and duration > 0 else None
        link_val = link if link and re.match(r'^https?://', str(link)) else None
        videos.append({'ResourceID': vid_id, 'Duration': dur or 0, 'Link': link_val})
        if filepath:
            notes.append({'ResourceID': vid_id, 'Body': _truncate_string(f'filepath:{filepath}', 2048)})

    # Documents
    for d in (data.get('documents') if isinstance(data, dict) else []) or []:
        doc_id = gen_id()
        title = d.get('title') if isinstance(d, dict) else None
        filepath = d.get('filepath') if isinstance(d, dict) else None
        url = d.get('url') if isinstance(d, dict) else None
        resources.append({
            'ResourceID': doc_id,
            'Date': today,
            'DateFor': today,
            'Author': 'khan accademy, lobster notes web scraper',
            'Topic': _truncate_string(title, 25),
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Pdf',
            'isVerified': False,
        })
        body = filepath or url or title or ''
        pdfs.append({'ResourceID': doc_id, 'Body': _truncate_string(body, 2048)})

    out = {
        'Resource': resources,
        'Note': notes,
        'pdf': pdfs,
        'Image': images,
        'Video': videos,
        'Website': websites,
    }
    with open(outpath,'w',encoding='utf-8') as f:
        json.dump(out,f,ensure_ascii=False,indent=2)


def start_driver():
    opts=Options(); opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=opts)

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('url'); p.add_argument('name', nargs='?'); return p.parse_args()

def main():
    
    URL_MAX_LENGTH = 2048 #ensures URL fits into DB

    args=parse_args(); url=args.url; outpath=args.name if args.name else ('data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.json')
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    d = start_driver(); d.get(url); time.sleep(1); html = d.page_source; d.quit()
    data = parse_page(url, html)
    write_json(data, outpath)
    out_dir = os.path.join(os.path.dirname(outpath) or '.', 'downloaded_videos')
    pdf_dir = os.path.join(os.path.dirname(outpath) or '.', 'downloadedPDFS')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    documents = []
    main_soup = BeautifulSoup(html, 'html.parser')
    for a_tag in main_soup.find_all('a', href=True):
        ahref = a_tag['href']
        if 'bit.ly' in ahref.lower() or 'bitly.com' in ahref.lower():
            if ahref.startswith('/'):
                ahref = combine_url(url, ahref)
            if 'IGNORE_LINKS' in globals() and ahref in IGNORE_LINKS:
                continue
            download_pdf(ahref, pdf_dir, documents)

    for link in data.get('links', []):
        ahref = link
        if ahref.startswith('/'):
            ahref = combine_url(url, ahref)
        if 'IGNORE_LINKS' in globals() and ahref in IGNORE_LINKS:
            continue
        if 'bit.ly' in ahref.lower() or 'bitly.com' in ahref.lower():
            download_pdf(ahref, pdf_dir, documents)
    
    
    video_urls = data.get('videos', [])
    video_data_list = []
    # build a set of existing video titles (normalized) to avoid duplicates
    existing_titles = set()
    if isinstance(data.get('videoData'), list):
        for v in data.get('videoData'):
            t = v.get('title') if isinstance(v, dict) else None
            if t:
                existing_titles.add(t.strip().lower())
    if video_urls:
        
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

            for embed_src in unique_embeds[:2]:
                try:                                    #prevents crashing for yt-dlp
                    print(f"Found YouTube embed: {embed_src} on page {vurl}")

                    # dl_cmd = [
                    #     'yt-dlp',
                    #     '--no-overwrites',
                    #     '-f', 'bestvideo+bestaudio/best',
                    #     '--merge-output-format', 'mkv',
                    #     embed_src,
                    #     '-o', os.path.join(out_dir, '%(title)s.%(ext)s'),
                    # ]
                    # actual video download disabled to avoid large downloads during scraping, but code is kept to allow possible future use
                    # subprocess.run(dl_cmd, check=True)

                    pf = subprocess.run(['yt-dlp', '--get-filename', '-o', '%(title)s.%(ext)s', embed_src], capture_output=True, text=True, check=True)
                    filename = pf.stdout.strip()
                    out_path = os.path.join(out_dir, filename)
                    

                    pj = subprocess.run(['yt-dlp', '--dump-json', embed_src], capture_output=True, text=True, check=True)
                    j = json.loads(pj.stdout)
                    title = j.get('title')
                    duration = j.get('duration')
                except subprocess.CalledProcessError as e:
                    print(f"Error {e}: Failed to get metadata for {embed_src}") 
                    continue
                except json.JSONDecodeError:
                    print(f"JSON output failed to parse for {embed_src}")
                    continue
                # normalize embed/watch/short URLs 
                normalized = _normalize_youtube_url(embed_src)
                #check to ensure URL will fit
                if len(normalized) > URL_MAX_LENGTH:
                    print(f"Link too long, shortening: {normalized[:50]}.")
                    short_link = normalized[:URL_MAX_LENGTH]
                else:
                    short_link = normalized
                video_entry = {
                    'title': title if title else (os.path.basename(out_path) if out_path else None),
                    'filepath': out_path,
                    #check to ensure metadata value is valid for duration
                    'duration': int(duration) if isinstance(duration, (int, float)) and duration > 0 else None,
                    'link': short_link,
                }
                # skip if title already seen 
                entry_title = video_entry.get('title') if isinstance(video_entry, dict) else None
                norm_title = entry_title.strip().lower() if entry_title else ''
                if norm_title and norm_title in existing_titles:
                    print(f"Skipping duplicate video by title: {entry_title}")
                else:
                    video_data_list.append(video_entry)
                    if norm_title:
                        existing_titles.add(norm_title)

            for a_tag in soup.find_all('a', href=True):
                ahref = a_tag['href']
                if 'bit.ly' in ahref.lower() or 'bitly.com' in ahref.lower():
                    if ahref.startswith('/'):
                        ahref = combine_url(vurl, ahref)
                    if 'IGNORE_LINKS' in globals() and ahref in IGNORE_LINKS:
                        continue
                    download_pdf(ahref, pdf_dir, documents)

        if video_data_list:
            data['videoData'] = video_data_list
            write_json(data, outpath)
        if documents:
            data['documents'] = data.get('documents', []) + documents
            write_json(data, outpath)

if __name__=='__main__': main()
