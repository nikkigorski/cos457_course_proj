#!/usr/bin/env python3
import argparse, json, time, os
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

if __name__=='__main__': main()
