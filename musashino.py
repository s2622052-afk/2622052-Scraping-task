import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import csv

start_url = 'https://www.musashino-u.ac.jp/'
domain = urlparse(start_url).netloc 

sitemap = {}
urls_to_visit = [start_url]
visited_urls = set()  

print("スクレイピングを開始します...")

while urls_to_visit:
    url = urls_to_visit.pop(0)

    if url in visited_urls:
        continue

    visited_urls.add(url)
    time.sleep(1) 

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            continue
        
        content_type = res.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            continue

        html_soup = BeautifulSoup(res.content, 'html.parser')

        title_tag = html_soup.find('title')
        if title_tag and title_tag.string:
            title_text = title_tag.string.strip()
        else:
            title_text = 'タイトルなし'

        sitemap[url] = title_text
        print(f"取得成功 [{len(sitemap)}]: {url} -> {title_text}")

        if len(sitemap) >= 10:
            print(f"{len(sitemap)}件のデータを取得")
            break

        a_list = html_soup.find_all('a')
        for a in a_list:
            href = a.get('href')
            if not href:
                continue

            full_url = urljoin(url, href)
            full_url = full_url.split('#')[0]

            parsed_href = urlparse(full_url)
            if parsed_href.netloc == domain:
                if full_url not in visited_urls and full_url not in urls_to_visit:
                    urls_to_visit.append(full_url)

    except Exception as e:
        print(f"エラー ({url}): {e}")
        continue

with open('musashino_sitemap.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['URL', 'Title']) 
    for u, t in sitemap.items():
        writer.writerow([u, t])