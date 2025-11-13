#!/usr/bin/env python3
import argparse, json, time, os
import datetime
import random
import urllib.parse
from decimal import Decimal
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    #files = []
    #pages = []
    
    note = []
    video = []
    website = []
    pdf = []
    image = []

    
    #file_extension = ('.pdf', '.mp4', '.jpg', '.png', '.doc')
    note_file_extension = ('.doc', '.txt', '.docx', '.rtf', '.tex', '.py', '.java')
    video_file_extension = ('.mp4', '.mov', '.avi', '.wmv', 'mp3', '.wav', '.aac', 'flac', '.ogg')
    pdf_file_extension = ('.pdf')
    image_file_extension = ('.jpg', '.png', '.gif', '.svg', '.bmp')

    


    for a in soup.find_all('a', href=True):
        h = a['href']
        h_full_url = combine_url(base_url, h)

        is_file = False
        # if h_full_url.lower().endswith(file_extension):
        #         files.append(h_full_url)
        #         h = combine_url(base_url, h)

        if h_full_url.lower().endswith(note_file_extension):
            note.append(h_full_url)
            # h = combine_url(base_url, h)
            is_file = True
        
        if h_full_url.lower().endswith(video_file_extension):
            video.append(h_full_url)
            # h = combine_url(base_url, h)
            is_file = True
        
        if h_full_url.lower().endswith(pdf_file_extension):
            pdf.append(h_full_url)
            # h = combine_url(base_url, h)
            is_file = True        
        
        if h_full_url.lower().endswith(image_file_extension):
            image.append(h_full_url)
            # h = combine_url(base_url, h)
            is_file = True        
        if not is_file and h_full_url.lower().startswith('http'):                       
            website.append(h_full_url)
    return {
        # 'files': list(dict.fromkeys(files)),
        'Note': list(dict.fromkeys(note)),
        'Video': list(dict.fromkeys(video)),
        'Image': list(dict.fromkeys(image)),
        'pdf': list(dict.fromkeys(pdf)),
        'Website': list(dict.fromkeys(website)),
    }

def parse_page(url, html):
    soup = BeautifulSoup(html,'html.parser')
    out={'url':url}
    out['title']=soup.title.string.strip() if soup.title and soup.title.string else None
    
    links_info = extract_links(soup, url)

    # static_media = []
    # vids = []

    # for url in links_info.get('files', []):
    #     if url.lower().endswith(('.mp4')):
    #         vids.append(url)
    #     else:
    #         static_media.append(url)
    
    out['Video'] = links_info.get('Video', [])
    out['Image'] = links_info.get('Image',[])
    out['pdf'] = links_info.get('pdf',[])
    out['Website'] = links_info.get('Website', [])
    out['Note'] = links_info.get('Note',[])

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

    used_ids = set()

    def gen_id():
        for _ in range(100000):
            c = random.randint(1, 2**31 - 1)
            if c not in used_ids:
                used_ids.add(c)
                return c
        raise RuntimeError('unable to generate unique id')

    page_title = data.get('title') if isinstance(data, dict) else None
    page_url = data.get('url') if isinstance(data, dict) else None

    # Page resource
    page_id = gen_id()
    resources.append({
        'ResourceID': page_id,
        'Date': today,
        'DateFor': today,
        'Author': 'mit ocw, lobster notes web scraper',
        'Topic': _truncate_string(page_title, 25) if page_title else None,
        'Keywords': None,
        'Rating': 9.9,
        'Format': 'Website',
        'isVerified': False,
    })
    if page_url and page_url.lower().startswith('http'):
        websites.append({'ResourceID': page_id, 'Link': page_url})

    # PDFs
    for p in (data.get('pdf') or []):
        pid = gen_id()
        resources.append({
            'ResourceID': pid,
            'Date': today,
            'DateFor': today,
            'Author': 'mit ocw, lobster notes web scraper',
            'Topic': None,
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Pdf',
            'isVerified': False,
        })
        pdfs.append({'ResourceID': pid, 'Body': p})

    # Images
    for img in (data.get('Image') or []):
        iid = gen_id()
        resources.append({
            'ResourceID': iid,
            'Date': today,
            'DateFor': today,
            'Author': 'mit ocw, lobster notes web scraper',
            'Topic': None,
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Image',
            'isVerified': False,
        })
        # img can be a URL string or a dict with url/width/height/size
        if isinstance(img, dict):
            link = img.get('url') or img.get('Link') or img.get('link')
            w = img.get('width') or img.get('Width')
            h = img.get('height') or img.get('Height')
            size_val = img.get('size') or img.get('Size')
            if size_val is None:
                try:
                    if isinstance(w, int) and isinstance(h, int):
                        size_val = int(w) * int(h)
                    elif isinstance(w, int):
                        size_val = int(w)
                    elif isinstance(h, int):
                        size_val = int(h)
                except Exception:
                    size_val = None
            if not isinstance(size_val, int) or size_val <= 0:
                size_val = 1
            images.append({'ResourceID': iid, 'Link': link, 'Size': size_val})
        else:
            images.append({'ResourceID': iid, 'Link': img, 'Size': 1})

    # Videos
    for v in (data.get('Video') or []):
        vid = gen_id()
        resources.append({
            'ResourceID': vid,
            'Date': today,
            'DateFor': today,
            'Author': 'mit ocw, lobster notes web scraper',
            'Topic': None,
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Video',
            'isVerified': False,
        })
        videos.append({'ResourceID': vid, 'Duration': None, 'Link': v})

    # Notes
    for n in (data.get('Note') or []):
        nid = gen_id()
        resources.append({
            'ResourceID': nid,
            'Date': today,
            'DateFor': today,
            'Author': 'mit ocw, lobster notes web scraper',
            'Topic': None,
            'Keywords': None,
            'Rating': 9.9,
            'Format': 'Note',
            'isVerified': False,
        })
        notes.append({'ResourceID': nid, 'Body': None})

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


def get_image_dimensions(url, driver=None, timeout=5):
    own_driver = False
    if not url:
        return 1, 1
    try:
        parsed = urllib.parse.urlparse(url)
        if not parsed.scheme:
            # assume https if missing
            url = 'https://' + url.lstrip('/')
    except Exception:
        pass
    if driver is None:
        driver = start_driver()
        own_driver = True
    try:
        script = '''
        const url = arguments[0];
        const timeout = arguments[1];
        const cb = arguments[arguments.length - 1];
        const img = document.createElement('img');
        let finished = false;
        img.onload = () => { if (!finished) { finished = true; cb({w: img.naturalWidth, h: img.naturalHeight}); } };
        img.onerror = () => { if (!finished) { finished = true; cb({w: 1, h: 1}); } };
        setTimeout(() => { if (!finished) { finished = true; cb({w: img.naturalWidth || 1, h: img.naturalHeight || 1}); } }, timeout*1000);
        img.src = url;
        '''
        res = driver.execute_async_script(script, url, timeout)
        w = int(res.get('w') or 1)
        h = int(res.get('h') or 1)
        if w <= 0: w = 1
        if h <= 0: h = 1
        return w, h
    except Exception:
        return 1, 1
    finally:
        if own_driver:
            try:
                driver.quit()
            except Exception:
                pass

def parse_args():
    p=argparse.ArgumentParser(); p.add_argument('url'); p.add_argument('name', nargs='?'); return p.parse_args()

def main():
    args=parse_args(); url=args.url; outpath=args.name if args.name else ('mit_data_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.json')
    os.makedirs(os.path.dirname(outpath) or '.', exist_ok=True)
    d = start_driver(); d.get(url); time.sleep(1); html = d.page_source
    data = parse_page(url, html)
    images = data.get('Image') or []
    images_updated = []
    for img_url in images:
        try:
            w, h = get_image_dimensions(img_url, driver=d, timeout=5)
            size = 1
            try:
                size = int(w) * int(h)
                if size <= 0:
                    size = 1
            except Exception:
                size = 1
            images_updated.append({'url': img_url, 'width': int(w), 'height': int(h), 'size': int(size)})
        except Exception:
            images_updated.append({'url': img_url, 'width': 1, 'height': 1, 'size': 1})
    data['Image'] = images_updated
    try:
        d.quit()
    except Exception:
        pass
    write_json(data, outpath)

if __name__=='__main__': main()
