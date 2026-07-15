import requests
from bs4 import BeautifulSoup
import json
import time
import os
from urllib.parse import urljoin

BASE_URL = "https://www.baranmoshavereh.com/"

CATEGORY_URLS = {
    "اخبار نظام وظیفه": "https://www.baranmoshavereh.com/category/%d9%86%d8%b8%d8%a7%d9%85-%d9%88%d8%b8%db%8c%d9%81%d9%87/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d9%86%d8%b8%d8%a7%d9%85-%d9%88%d8%b8%db%8c%d9%81%d9%87/",
    "تحصیلی": "https://www.baranmoshavereh.com/category/%d8%aa%d8%ad%d8%b5%db%8c%d9%84%db%8c/",
    "اخبار تحصیلی": "https://www.baranmoshavereh.com/category/%d8%aa%d8%ad%d8%b5%db%8c%d9%84%db%8c/%d8%a7%d8%ae%d8%a8%d8%a7%d8%b1-%d8%aa%d8%ad%d8%b5%db%8c%d9%84%db%8c/",
    "معافیت پزشکی": "https://www.baranmoshavereh.com/category/%d9%86%d8%b8%d8%a7%d9%85-%d9%88%d8%b8%db%8c%d9%81%d9%87/%d9%85%d8%b9%d8%a7%d9%81%db%8c%d8%aa-%d9%be%d8%b2%d8%b4%da%a9%db%8c/",
    "امریه": "https://www.baranmoshavereh.com/category/%d9%86%d8%b8%d8%a7%d9%85-%d9%88%d8%b8%db%8c%d9%81%d9%87/%d8%a7%d9%85%d8%b1%db%8c%d9%87/",
    "خدمت سربازی": "https://www.baranmoshavereh.com/category/%d9%86%d8%b8%d8%a7%d9%85-%d9%88%d8%b8%db%8c%d9%81%d9%87/%d8%ae%d8%af%d9%85%d8%aa-%d8%b3%d8%b1%d8%a8%d8%a7%d8%b2%db%8c/",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

REQUEST_DELAY = 1.0
MAX_RETRIES = 3
CHECKPOINT_EVERY = 25
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "baranmoshavereh_articles.json")
URLS_JSON = os.path.join(OUTPUT_DIR, "baranmoshavereh_article_urls.json")

REMOVE_SELECTORS = [
    "script", "style", "video", "form",
    ".banner-tamas-wrapper-back", ".baranCallToAction-wrapper",
    ".wpb_raw_html", ".vc_cta3-container", ".post-share",
]


def get_soup(url: str) -> BeautifulSoup:
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding
            return BeautifulSoup(resp.text, "html.parser")
        except Exception as e:
            last_error = e
            time.sleep(2 * (attempt + 1))
    raise last_error


def extract_list_items(soup: BeautifulSoup) -> list[dict]:
    items = []
    blocks = soup.select("article.type-post, div.type-post.listing-item")

    for block in blocks:
        title_el = block.select_one(".title a, h2.title a, h3.title a")
        if not title_el:
            continue

        href = title_el.get("href")
        if not href:
            continue

        title = title_el.get_text(strip=True)
        url = urljoin(BASE_URL, href)

        summary_el = block.select_one(".post-summary")
        summary = summary_el.get_text(strip=True) if summary_el else ""

        date_el = block.select_one(".post-meta time.post-published")
        date = date_el.get("datetime", "") if date_el else ""

        items.append({
            "url": url,
            "list_title": title,
            "list_summary": summary,
            "list_date": date,
        })

    return items


def find_next_page(soup: BeautifulSoup) -> str | None:
    next_el = soup.select_one(".pagination a.next.page-numbers")
    if next_el and next_el.get("href"):
        return urljoin(BASE_URL, next_el["href"])
    return None


def crawl_category(category_name: str, start_url: str) -> list[dict]:
    items = []
    url = start_url
    seen_pages = set()
    page_num = 1

    while url and url not in seen_pages:
        seen_pages.add(url)
        soup = get_soup(url)
        page_items = extract_list_items(soup)
        for it in page_items:
            it["category"] = category_name
        print(f"    صفحه {page_num}: {len(page_items)} مقاله")
        items.extend(page_items)
        url = find_next_page(soup)
        page_num += 1
        time.sleep(REQUEST_DELAY)

    return items


def collect_all_article_links() -> list[dict]:
    merged = {}

    for category_name, start_url in CATEGORY_URLS.items():
        print(f"در حال پیمایش دسته: {category_name}")
        items = crawl_category(category_name, start_url)

        for it in items:
            if it["url"] not in merged:
                merged[it["url"]] = {
                    "url": it["url"],
                    "list_title": it["list_title"],
                    "list_summary": it["list_summary"],
                    "list_date": it["list_date"],
                    "categories": [it["category"]],
                }
            else:
                if it["category"] not in merged[it["url"]]["categories"]:
                    merged[it["url"]]["categories"].append(it["category"])

    return list(merged.values())


def extract_comment_node(li) -> dict:
    own_div = li.find("div", class_="clearfix", recursive=False)

    author_el = own_div.select_one(".comment-author")
    author = author_el.get_text(strip=True).replace("says", "").strip() if author_el else ""

    date_el = own_div.select_one("time.comment-published")
    date = date_el.get("datetime", "") if date_el else ""

    content_el = own_div.select_one(".comment-content")
    text = content_el.get_text(separator=" ", strip=True) if content_el else ""

    is_staff = "comment-author-modir" in li.get("class", []) or author == "باران مشاوره"

    replies = []
    children_ol = li.find("ol", class_="children", recursive=False)
    if children_ol:
        for reply_li in children_ol.find_all("li", class_="comment", recursive=False):
            replies.append(extract_comment_node(reply_li))

    return {
        "author": author,
        "date": date,
        "text": text,
        "is_staff": is_staff,
        "replies": replies,
    }


def extract_comments(soup: BeautifulSoup) -> list[dict]:
    comments = []
    comment_list = soup.select_one("ol.comment-list")
    if not comment_list:
        return comments

    for li in comment_list.find_all("li", class_="comment", recursive=False):
        comments.append(extract_comment_node(li))

    return comments


def extract_article(url: str) -> dict:
    soup = get_soup(url)

    title_el = soup.select_one("h1.single-post-title .post-title")
    title = title_el.get_text(strip=True) if title_el else ""

    subtitle_el = soup.select_one("h2.post-subtitle")
    subtitle = subtitle_el.get_text(strip=True) if subtitle_el else ""

    content_el = soup.select_one(".entry-content.single-post-content")
    content = ""
    if content_el:
        for sel in REMOVE_SELECTORS:
            for el in content_el.select(sel):
                el.decompose()
        content = content_el.get_text(separator="\n", strip=True)

    tags = [a.get_text(strip=True) for a in soup.select(".entry-terms.post-tags a")]
    comments = extract_comments(soup)

    return {
        "url": url,
        "title": title,
        "subtitle": subtitle,
        "content": content,
        "tags": tags,
        "comments": comments,
    }


def load_existing_results() -> dict:
    if not os.path.exists(OUTPUT_JSON):
        return {}
    try:
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {r["url"]: r for r in data}
    except Exception:
        return {}


def save_results(results_by_url: dict):
    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(list(results_by_url.values()), f, ensure_ascii=False, indent=2)
    except PermissionError as e:
        print(f"خطا در نوشتن {OUTPUT_JSON}: {e}")


def main():
    if os.path.exists(URLS_JSON):
        print(f"استفاده از لیست لینک‌های ذخیره‌شده: {URLS_JSON}")
        with open(URLS_JSON, "r", encoding="utf-8") as f:
            article_links = json.load(f)
    else:
        article_links = collect_all_article_links()
        with open(URLS_JSON, "w", encoding="utf-8") as f:
            json.dump(article_links, f, ensure_ascii=False, indent=2)

    print(f"تعداد کل مقالات یکتا: {len(article_links)}")

    results_by_url = load_existing_results()
    print(f"تعداد مقالات از قبل استخراج‌شده: {len(results_by_url)}")

    remaining = [item for item in article_links if item["url"] not in results_by_url]
    print(f"تعداد مقالات باقی‌مانده برای استخراج: {len(remaining)}")

    for i, item in enumerate(remaining, start=1):
        print(f"  [{i}/{len(remaining)}] {item['url']}")
        try:
            article = extract_article(item["url"])
            article["categories"] = item["categories"]
            article["list_summary"] = item["list_summary"]
            article["list_date"] = item["list_date"]
            results_by_url[item["url"]] = article
        except Exception as e:
            print(f"    خطا: {e}")

        if i % CHECKPOINT_EVERY == 0:
            save_results(results_by_url)
            print(f"    checkpoint ذخیره شد ({len(results_by_url)} رکورد)")

        time.sleep(REQUEST_DELAY)

    save_results(results_by_url)
    print(f"\nپایان. {len(results_by_url)} رکورد ذخیره شد در {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
