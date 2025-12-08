#!/usr/bin/env python3
"""
Minimal Quizlet scraper helper
- Usage: quizlet_scraper.py <url> [out_base]
- Saves rendered HTML to <out_base>.html and extracted page text to <out_base>.txt

This is intentionally small: it uses Selenium to render the page (JS) and BeautifulSoup
only to extract visible/textual content for inspection.
"""
import argparse
import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def start_driver():
    opts = Options()
    # use new headless mode where available; safe flags for container environments
    opts.add_argument('--headless=new')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=opts)


def parse_args():
    p = argparse.ArgumentParser(description='Minimal Quizlet page dumper (Selenium + BeautifulSoup).')
    p.add_argument('url', help='URL to fetch')
    p.add_argument('out', nargs='?', help='output base path (no extension). Default: quizlet_scrape_<ts>', default=None)
    return p.parse_args()


def main():
    args = parse_args()
    url = args.url
    outbase = args.out if args.out else ('quizlet_scrape_' + time.strftime('%Y-%m-%d_%H-%M-%S'))
    outdir = os.path.dirname(outbase) or '.'
    os.makedirs(outdir, exist_ok=True)

    driver = start_driver()
    html = ''
    try:
        driver.get(url)
        # give the page a moment to load dynamic content
        time.sleep(2)
        html = driver.page_source
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(separator='\n', strip=True)

    html_path = outbase + '.html'
    txt_path = outbase + '.txt'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f'Saved rendered HTML -> {html_path}')
    print(f'Saved extracted text -> {txt_path}')


if __name__ == '__main__':
    main()
