import requests, os, re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

base_url = "https://muctieu2025.my.canva.site"
html_url = f"{base_url}/index.html"

download_root = "_assets"
os.makedirs(download_root, exist_ok=True)

def save_file(url):
    parsed = urlparse(url)
    path = parsed.path.lstrip("/")
    local_path = os.path.join(download_root, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(r.content)
            print(f"[+] {local_path}")
            return r.text if url.endswith(('.js','.css','.html')) else None
        else:
            print(f"[-] {local_path} ({r.status_code})")
    except Exception as e:
        print(f"[!] {local_path}: {e}")
    return None

# tải html
r = requests.get(html_url)
r.raise_for_status()
html = r.text
save_file(html_url)

# parse html + regex _assets
soup = BeautifulSoup(html, "html.parser")
assets = set()

for tag in soup.find_all(['script','link','img']):
    attr = tag.get('src') or tag.get('href')
    if attr:
        assets.add(urljoin(base_url+'/', attr))

assets.update(urljoin(base_url+'/', m) for m in re.findall(r'[_/]{0,1}_assets/[a-zA-Z0-9_\-./]+', html))

# scan js/css
to_scan = list(assets)
scanned = set()
while to_scan:
    u = to_scan.pop()
    if u in scanned:
        continue
    scanned.add(u)
    content = save_file(u)
    if content:
        new_assets = [urljoin(base_url+'/', m) for m in re.findall(r'[_/]{0,1}_assets/[a-zA-Z0-9_\-./]+', content)]
        for n in new_assets:
            if n not in scanned:
                to_scan.append(n)

