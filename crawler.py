import os
import logging
import threading
import requests
from time import sleep
from bs4 import BeautifulSoup
from collections import deque
from url_normalize import url_normalize
from urllib.parse import urlparse, urljoin, urldefrag
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from utils import configure_logging, save_state, load_state, url_to_path
import concurrent.futures


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
}


def soup_maker(url: str) -> BeautifulSoup:
    """输入url，使用requests库抓取取网页内容，返回BeautifulSoup对象

    Args:
        url (str): 目标网页

    Returns:
        BeautifulSoup: bs4.BeautifulSoup 对象
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = response.apparent_encoding
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP error: {e} - URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error: {e} - URL: {url}")
        return None

    html_doc = response.text
    soup = BeautifulSoup(html_doc, "html.parser")
    return soup


def save_soup(soup: BeautifulSoup, url: str, save_path: str) -> None:
    """按照url路径将soup对象保存为html文件

    Args:
        soup (BeautifulSoup): _description_
        url (str): _description_
        save_path (str): 根目录，网页的域名
    """
    parsed_url = urlparse(url)
    path = parsed_url.path.strip("/")
    if not path:  # 如果 URL 没有路径，将其保存为 index.html
        path = "index.html"
    else:
        path = os.path.join(path, "index.html")

    try:
        save_dir = os.path.join(save_path, os.path.dirname(path))
        os.makedirs(save_dir, exist_ok=True)

        save_file_path = os.path.join(save_dir, os.path.basename(path))
        with open(save_file_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

    except FileExistsError as e:
        logging.error(f"File exists error: {e} - URL: {url} - path:{save_dir}")


def links_scraper_sp(soup: BeautifulSoup, url: str, domain: str) -> set:
    """提取单个网页中的所有链接，添加过滤规则，比如必须在指定域名domain下，必须是.html后缀等

    Args:
        soup (BeautifulSoup): 页面的soup对象
        url (str): 页面的url，用来拼接绝对目录（链接）
        domain (str): 指定的域名（下要的所有链接）

    Returns:
        set: 返回页面下爬到的所有链接（集合）
    """
    all_links = set()
    for anchor in soup.find_all("a"):
        href = anchor.attrs.get("href")

        if href:
            href, _ = urldefrag(href)
            if not href.startswith(("http://", "https://", "//")):
                href = urljoin(url, href)
            if not href.startswith(domain):
                continue
            
            parsed_href = urlparse(href)
            if not (
                parsed_href.path.endswith((".html", ".htm", "/"))
                or "." not in parsed_href.path
            ):
                continue

            all_links.add(url_normalize(href))

    return all_links


def process_link(
    current_url: str,
    current_depth: int,
    domain: str,
    save_path: str,
    fp_links: set,
    max_depth: int,
    lock: threading.Lock  # 新增参数
) -> tuple:
    """bfs 并行处理链接的模块

    Args:
        current_url (str): 当前要处理的url
        current_depth (int): 当前url所在的深度
        domain (str): 当前网站的根域名
        save_path (str): html保存路径
        fp_links (set): 已经处理过的链接
        max_depth (int): 最大深度

    Returns:
        tuple: (新链接，下一层深度)
    """
    with lock:
        if current_url in fp_links or current_depth > max_depth:
            return None, None

    soup = soup_maker(current_url)
    if soup is None:
        return None, None

    save_soup(soup.prettify(), current_url, save_path)
    with lock:
        fp_links.add(current_url)

    if current_depth < max_depth:
        found_links = links_scraper_sp(soup=soup, url=current_url, domain=domain)
        new_links = found_links - fp_links
        return new_links, current_depth + 1

    return None, None


def links_scraper_bfs_parallel(
    url: str, domain: str, save_path: str, max_depth: int = 12, max_workers: int = 6
)->None:
    """bfs并行爬虫；使用ThreadPoolExecutor；支持断点续爬，使用pickle保存状态；爬取情况会记录在save_path/crawler.log中

    Args:
        url (str): 爬虫的起点url
        domain (str): 想要域名
        save_path (str): 保存的base路径
        max_depth (int, optional): bfs最大深度. Defaults to 12.
        max_workers (int, optional): 并行数量. Defaults to 6.
    """
    configure_logging(save_path)
    fp_links, queue = load_state(save_path)

    if not queue:
        queue = deque([(url, 0)])
    if not fp_links:
        fp_links = set()

    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        while queue or futures:
            while queue:
                current_url, current_depth = queue.popleft()
                future = executor.submit(
                    process_link,
                    current_url,
                    current_depth,
                    domain,
                    save_path,
                    fp_links,
                    max_depth,
                    lock,
                )
                futures.append(future)

            for future in as_completed(futures):
                futures.remove(future)
                result = future.result()
                if result:
                    new_links, next_depth = result
                    if new_links:
                        queue.extend([(link, next_depth) for link in new_links])
                sleep(0.1)

            save_state(fp_links, queue, save_path)

        wait(futures)