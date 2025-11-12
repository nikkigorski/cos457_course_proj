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
import struct
import io

IGNORE_FILE = os.path.join(os.path.dirname(__file__), 'ignore_links.json')
try:
    with open(IGNORE_FILE, 'r', encoding='utf-8') as _f:
        _ignore_data = json.load(_f)
        IGNORE_LINKS = set(_ignore_data.get('links', []))
except Exception:
    IGNORE_LINKS = set()

try:
    _words = _ignore_data.get('words') if '_ignore_data' in globals() and isinstance(_ignore_data, dict) else None
    if not _words:
        _words = _ignore_data.get('ignore_words') if '_ignore_data' in globals() and isinstance(_ignore_data, dict) else None
    IGNORE_WORDS = set(w.lower() for w in (_words or []))
except Exception:
    IGNORE_WORDS = set()


def should_ignore_link(href, anchor_text=None):
    if not href:
        return True
    try:
        low = href.lower()
    except Exception:
        low = ''
    if 'IGNORE_LINKS' in globals() and IGNORE_LINKS and href in IGNORE_LINKS:
        return True
    if 'IGNORE_WORDS' in globals() and IGNORE_WORDS:
        for w in IGNORE_WORDS:
            if w and w in low:
                return True
    if anchor_text:
        try:
            at = anchor_text.lower()
            for w in IGNORE_WORDS:
                if w and w in at:
                    return True
        except Exception:
            pass
    return False

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


def get_image_dimensions(url, driver=None, timeout=5):
    
    if not url or not isinstance(url, str) or not url.lower().startswith('http'):
        return 1, 1

    own_driver = False
    if driver is None:
        try:
            driver = start_driver()
            own_driver = True
        except Exception:
            return 1, 1

    try:
        try:
            driver.set_script_timeout(timeout)
        except Exception:
            pass

        # Use execute_async_script to load the image and wait for it to load
        try:
            res = driver.execute_async_script(
                """
                var src = arguments[0];
                var cb = arguments[arguments.length - 1];
                try {
                    var img = new Image();
                    img.onload = function() { cb([img.naturalWidth || 1, img.naturalHeight || 1]); };
                    img.onerror = function() { cb([1, 1]); };
                    img.src = src;
                } catch (e) {
                    cb([1, 1]);
                }
                """,
                url
            )
        except Exception:
            return 1, 1

        if isinstance(res, (list, tuple)) and len(res) >= 2:
            try:
                w = int(res[0]) if res[0] else 1
            except Exception:
                w = 1
            try:
                h = int(res[1]) if res[1] else 1
            except Exception:
                h = 1
            # enforce minimum 1
            return (w if w >= 1 else 1, h if h >= 1 else 1)
        return 1, 1
    finally:
        if own_driver:
            try:
                driver.quit()
            except Exception:
                pass


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


def record_pdf_link(href, base_url, documents):
    if not href:
        return documents
    is_bitly = 'bit.ly' in href.lower() or 'bitly.com' in href.lower()
    if ('.pdf' not in href.lower()) and (not is_bitly):
        return documents
    if href.startswith('/'):
        href = combine_url(base_url, href)

    final = href
    if is_bitly:
        try:
            req = urllib.request.Request(href, method='HEAD')
            with urllib.request.urlopen(req, timeout=15) as resp:
                final = resp.geturl()
        except Exception:
            final = href
    parsed = urllib.parse.urlparse(final)
    if '.pdf' not in final.lower():
        return documents

    name = os.path.basename(parsed.path)
    name = urllib.parse.unquote(name) if name else None
    name = name.replace('%', ' ').replace('_', ' ').strip() if name else None
    if not name:
        name = 'document.pdf'
    if not name.lower().endswith('.pdf'):
        name = f"{name}.pdf"
    documents.append({'title': name, 'filepath': None, 'url': final})
    return documents

def extract_links(soup, base_url):
    ex = []
    others = []
    vids = []
    for a in soup.find_all('a', href=True):
        h = a['href']
        anchor_text = a.get_text() or a.get('title') or ''
        if h.startswith('/'):
            h = combine_url(base_url, h)
            if should_ignore_link(h, anchor_text):
                continue
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

    ex = [u for u in ex if not should_ignore_link(u)]
    others = [u for u in others if not should_ignore_link(u)]
    vids = [u for u in vids if not should_ignore_link(u)]

    return {
        'exercises': ex,
        'links': others,
        'videos_from_links': vids,
    }

def parse_page(url, html, driver=None):
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
    # Ensure any anchor on the page containing '/v/' (Khan video pages) is treated as a video page
    try:
        for a in soup.find_all('a', href=True):
            h = a['href']
            if h.startswith('/'):
                h = combine_url(url, h)
            if '/v/' in (h or '').lower():
                if not should_ignore_link(h, a.get_text() or a.get('title')):
                    vids.append(h)
    except Exception:
        pass
    if vids:
        seen = set(); merged = []
        for u in vids:
            if u not in seen:
                merged.append(u); seen.add(u)
        out['videos'] = merged
    out['exercises'] = links_info.get('exercises', [])
    out['links'] = links_info.get('links', [])
    imgs = []
    for img in soup.find_all('img', src=True):
        src = img['src']
        if src.startswith('/'):
            src = combine_url(url, src)
        if should_ignore_link(src):
            continue
        alt = img.get('alt') or img.get('title')
        w, h = get_image_dimensions(src, driver=driver)
        imgs.append({'url': src, 'alt': alt, 'width': w, 'height': h})
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/'):
            href = combine_url(url, href)
        low = href.lower()
        if re.search(r"\.(jpg|jpeg|png|gif|svg|webp)(?:$|[?#])", low):
            if should_ignore_link(href):
                continue
            alt = a.get_text().strip() if a.get_text() else None
            w, h = get_image_dimensions(href, driver=driver)
            imgs.append({'url': href, 'alt': alt, 'width': w, 'height': h})
   
    seen_i = set(); uniq_imgs = []
    for it in imgs:
        u = it.get('url')
        if not u:
            continue
        if u in seen_i:
            continue
        seen_i.add(u)
        uniq_imgs.append(it)
    out['images'] = uniq_imgs
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
        for _ in range(2**31):
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

    # Images
    for im in (data.get('images') if isinstance(data, dict) else []) or []:
        img_id = gen_id()
        img_url = im.get('url') if isinstance(im, dict) else None
        alt = im.get('alt') if isinstance(im, dict) else None
        topic = None
        if alt:
            topic = _truncate_string(alt, 25)
        else:
            try:
                parsed = urllib.parse.urlparse(img_url) if img_url else None
                bn = os.path.basename(parsed.path) if parsed and parsed.path else None
                topic = _truncate_string(bn, 25) if bn else None
            except Exception:
                topic = None

        resources.append({
            'ResourceID': img_id,
            'Date': today,
            'DateFor': today,
            'Author': 'khan accademy, lobster notes web scraper',
            'Topic': topic,
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Image',
            'isVerified': False,
        })
        if img_url and re.match(r'^https?://', str(img_url)):
            w = im.get('width') if isinstance(im, dict) else None
            h = im.get('height') if isinstance(im, dict) else None
            entry = {'ResourceID': img_id, 'Link': img_url}
            if isinstance(w, int):
                entry['Width'] = w
            if isinstance(h, int):
                entry['Height'] = h
            images.append(entry)
        if alt:
            notes.append({'ResourceID': img_id, 'Body': _truncate_string(alt, 2048)})

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

    args=parse_args(); url=args.url; outpath=args.name if args.name else ('khan_data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.json')
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    d = start_driver(); d.get(url); time.sleep(1); html = d.page_source
    data = parse_page(url, html, driver=d)
    write_json(data, outpath)
    out_dir = os.path.join(os.path.dirname(outpath) or '.', 'downloaded_videos')
    pdf_dir = os.path.join(os.path.dirname(outpath) or '.', 'downloadedPDFS')
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(pdf_dir, exist_ok=True)
    documents = []
    images = []
    seen_images = set()
    main_soup = BeautifulSoup(html, 'html.parser')
    for a_tag in main_soup.find_all('a', href=True):
        ahref = a_tag['href']
        if ahref.startswith('/'):
            ahref = combine_url(url, ahref)
        if should_ignore_link(ahref):
            continue
        if '.pdf' in ahref.lower() or 'bit.ly' in ahref.lower() or 'bitly.com' in ahref.lower():
            documents=record_pdf_link(ahref, url, documents)
        if re.search(r"\.(jpg|jpeg|png|gif|svg|webp)(?:$|[?#])", ahref.lower()):
            if ahref not in seen_images:
                w, h = get_image_dimensions(ahref, driver=d)
                seen_images.add(ahref)
                images.append({'url': ahref, 'alt': a_tag.get_text().strip() or None, 'width': w, 'height': h})
    
    for link in data.get('links', []):
        ahref = link
        if ahref.startswith('/'):
            ahref = combine_url(url, ahref)
        if should_ignore_link(ahref):
            continue
        if '.pdf' in ahref.lower() or 'bit.ly' in ahref.lower() or 'bitly.com' in ahref.lower():
            documents=record_pdf_link(ahref, url, documents)
    
    
    video_queue = list(data.get('videos') or [])
    video_data_list = []
    # build a set of existing video titles (normalized) to avoid duplicates
    existing_titles = set()
    if isinstance(data.get('videoData'), list):
        for v in data.get('videoData'):
            t = v.get('title') if isinstance(v, dict) else None
            if t:
                existing_titles.add(t.strip().lower())

    visited_video_pages = set()
    while video_queue:
        vurl = video_queue.pop(0)
        if not vurl:
            continue
        if vurl.startswith('/'):
            vurl = combine_url(url, vurl)
        if should_ignore_link(vurl):
            continue
        low = vurl.lower()
        # If this is a Khan video page (/v/), fetch and parse it to discover embedded video URLs
        if '/v/' in low and vurl not in visited_video_pages:
            visited_video_pages.add(vurl)
            try:
                d = start_driver()
                d.get(vurl)
                time.sleep(1)
                vhtml = d.page_source
                parsed = parse_page(vurl, vhtml, driver=d)
                d.quit()
            except Exception:
                try:
                    d.quit()
                except Exception:
                    pass
                continue
            # collect any images found on the video page
            for img in parsed.get('images', []) or []:
                img_url = img.get('url') if isinstance(img, dict) else None
                if img_url and not should_ignore_link(img_url) and img_url not in seen_images:
                    seen_images.add(img_url)
                    images.append(img)
            # collect any documents found on the video page
            for doc in parsed.get('documents', []) or []:
                doc_url = doc.get('url') if isinstance(doc, dict) else None
                if doc_url and not should_ignore_link(doc_url):
                    documents = record_pdf_link(doc_url, vurl, documents)
            
            for nv in parsed.get('videos', []) or []:
                if nv and nv not in video_queue and nv not in visited_video_pages:
                    video_queue.append(nv)
            continue

        try:
            driver = start_driver()
            driver.get(vurl)
            time.sleep(1)
            page_html = driver.page_source
            soup = BeautifulSoup(page_html, 'html.parser')
        except Exception:
            try:
                driver.quit()
            except Exception:
                pass
            continue
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
            try:
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
                pass
            else:
                video_data_list.append(video_entry)
                if norm_title:
                    existing_titles.add(norm_title)
        for img in soup.find_all('img', src=True):
            src = img['src']
            if src.startswith('/'):
                src = combine_url(vurl, src)
            if should_ignore_link(src):
                continue
            if src not in seen_images:
                seen_images.add(src)
                w, h = get_image_dimensions(src, driver=driver)
                images.append({'url': src, 'alt': img.get('alt') or img.get('title'), 'width': w, 'height': h})
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/'):
                href = combine_url(vurl, href)
            low = href.lower()
            if re.search(r"\.(jpg|jpeg|png|gif|svg|webp)(?:$|[?#])", low):
                if should_ignore_link(href, a.get_text() or a.get('title')):
                    continue
                if href not in seen_images:
                    seen_images.add(href)
                    w, h = get_image_dimensions(href, driver=driver)
                    images.append({'url': href, 'alt': a.get_text().strip() if a.get_text() else None, 'width': w, 'height': h})
        try:
            driver.quit()
        except Exception:
            pass

    if video_data_list:
        data['videoData'] = video_data_list
        if images:
            data['images'] = (data.get('images', []) or []) + images
        write_json(data, outpath)
    if documents:
        data['documents'] = data.get('documents', []) + documents
        if images:
            data['images'] = (data.get('images', []) or []) + images
        write_json(data, outpath)
    elif images:
        data['images'] = (data.get('images', []) or []) + images
        write_json(data, outpath)

  
if __name__=='__main__': main()
