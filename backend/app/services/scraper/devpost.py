# Scraper module for IdeaSurf - scraping Devpost's winning hackathon database
"""
Will use the uploaded URL to scrape devpost project pages for relevant fields and output to a JSON file.

Usage:
  python3 devpost.py --pages 24 --listing-url "https://devpost.com/software/search?query=is%3Afeatured"

Outputs a JSON file `devpost_dump.json` by default.
"""

from __future__ import annotations
import argparse
import json
import random
import time
import re
from datetime import datetime
from urllib.parse import urlparse
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver(headless: bool = True) -> webdriver.Chrome:
    opts = Options()
    if headless:
        # use new headless mode when available
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1200,2000")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--blink-settings=imagesEnabled=false")
    opts.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(45)
    return driver


def p_sleep(a: float = 0.6, b: float = 1.6) -> None:
    time.sleep(random.uniform(a, b))


def accept_cookies_if_present(driver: webdriver.Chrome) -> None:
    try:
        for sel in [
            "#onetrust-accept-btn-handler",
            "button#onetrust-accept-btn-handler",
            "button[aria-label*='Accept']",
            "button.cookie-accept",
        ]:
            btns = driver.find_elements(By.CSS_SELECTOR, sel)
            if btns:
                try:
                    btns[0].click()
                except Exception:
                    pass
                return
        # fallback by text
        for b in driver.find_elements(By.TAG_NAME, "button"):
            if "accept" in (b.text or "").lower():
                try:
                    b.click()
                except Exception:
                    pass
                return
    except Exception:
        pass

# Will return True if the URL is a valid Devpost project URL, False otherwise.
def is_project_url(u: str) -> bool:
    try:
        p = urlparse(u)
        if p.netloc not in ("devpost.com", "www.devpost.com"):
            return False
        if not p.path.startswith("/software/"):
            return False
        segs = [s for s in p.path.split("/") if s]
        if len(segs) != 2:
            return False
        slug = segs[1]
        banned = {"built-with", "search", "popular", "new"}
        if slug in banned:
            return False
        if p.query:
            return False
        return True
    except Exception:
        return False


def collect_project_links(driver: webdriver.Chrome, pages: int = 24, min_anchors: int = 20, listing_url: Optional[str] = None) -> list[str]:
    """Collect unique project detail URLs from a paginated listing.

    Behavior:
    - If listing_url is provided it will be used as base and `page=` appended.
    - Will iterate pages 1..pages and stop early if a page yields zero new project links.
    """
    all_links = set()
    wait = WebDriverWait(driver, 20)

    for page in range(1, pages + 1):
        base = listing_url or "https://devpost.com/software/"
        sep = "&" if "?" in base else "?"
        url = f"{base}{sep}page={page}"
        print(f"[list] GET {url}")
        driver.get(url)

        accept_cookies_if_present(driver)
        # nudge lazy load
        try:
            driver.execute_script("window.scrollTo(0, 700);")
        except Exception:
            pass

        try:
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "a[href*='/software/']")) >= min_anchors)
        except TimeoutException:
            # still try to collect whatever anchors are present
            pass

        raw_links = [a.get_attribute("href") for a in driver.find_elements(By.CSS_SELECTOR, "a[href*='/software/']")]
        page_links = {u for u in raw_links if u and is_project_url(u)}
        new_links = page_links - all_links
        print(f"Page {page}: found {len(page_links)} project anchors, {len(new_links)} new")
        all_links |= page_links

        p_sleep()

        # stop early if nothing new on this page
        if not new_links:
            print("No new links found on this page; stopping early.")
            break

    print(f"Total unique project URLs collected: {len(all_links)}")
    return sorted(all_links)


def norm_tag(t: str) -> str:
    t = t.strip().lower()
    t = re.sub(r"[^a-z0-9\+\.\#\-]+", "-", t)
    return t.strip("-")


# Extract "Built With" tags from the project page to append to "tags" list on upload.
def extract_built_with(driver: webdriver.Chrome) -> list[str]:
    tags = set()
    sel_list = [
        "section#built-with a", "section#built-with li",
        ".built-with a", ".built-with li",
        "ul#built-with a", "ul#built-with li",
        ".tags a[href*='/software/built-with/']",
    ]
    for sel in sel_list:
        for el in driver.find_elements(By.CSS_SELECTOR, sel):
            txt = (el.text or "").strip()
            href = el.get_attribute("href") or ""
            if "/software/built-with/" in href:
                slug = urlparse(href).path.rsplit("/", 1)[-1]
                if slug:
                    tags.add(norm_tag(slug))
                    continue
            if txt:
                tags.add(norm_tag(txt))

    # header-based fallback
    for h in driver.find_elements(By.XPATH, "//h2|//h3"):
        if (h.text or "").strip().lower() == "built with":
            for sib in h.find_elements(By.XPATH, "following-sibling::*"):
                if sib.tag_name.lower() in {"h1","h2","h3","h4","h5"}:
                    break
                for el in sib.find_elements(By.XPATH, ".//a|.//li|.//span"):
                    if (el.text or "").strip():
                        tags.add(norm_tag(el.text.strip()))
            break

    return sorted(t for t in tags if t)

# Extract text under specific section headings like "What it does" for long description.
def extract_section_text(driver: webdriver.Chrome, heading_texts=("what it does",)) -> Optional[str]:
    targets = {h.lower().rstrip(":") for h in heading_texts}
    headers = driver.find_elements(By.XPATH, "//h1|//h2|//h3|//h4|//h5")
    for h in headers:
        label = (h.text or "").strip().lower().rstrip(":")
        if label in targets:
            parts = []
            for sib in h.find_elements(By.XPATH, "following-sibling::*"):
                tag = sib.tag_name.lower()
                if tag in ("h1", "h2", "h3", "h4", "h5"):
                    break
                for p in sib.find_elements(By.TAG_NAME, "p"):
                    if p.text.strip():
                        parts.append(p.text.strip())
                for li in sib.find_elements(By.TAG_NAME, "li"):
                    if li.text.strip():
                        parts.append("• " + li.text.strip())
                if not parts and sib.text.strip():
                    parts.append(sib.text.strip())
            text = "\n".join(parts).strip()
            if text:
                return text

    # container-based fallback
    alt = driver.find_elements(
        By.XPATH,
        "//*[self::section or self::div]["
        "contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what-it-does') or "
        "contains(translate(@data-section,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what-it-does') or "
        "contains(translate(@data-tab,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what-it-does')]"
    )
    for container in alt:
        parts = []
        for p in container.find_elements(By.TAG_NAME, "p"):
            if p.text.strip():
                parts.append(p.text.strip())
        for li in container.find_elements(By.TAG_NAME, "li"):
            if li.text.strip():
                parts.append("• " + li.text.strip())
        if parts:
            return "\n".join(parts).strip()

    return None


# Scrape a single Devpost project page for relevant fields.
def scrape_project(driver: webdriver.Chrome, url: str) -> dict:
    d = {
        "name": None,
        "short_description": None,
        "long_description": None,
        "url": url,
        "source": "Devpost",
        "tags": [],
        "created_at": None,
    }

    driver.get(url)
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1, h2")))
        title_el = driver.find_element(By.CSS_SELECTOR, "h1#app-title, h1.title, h1")
        d["name"] = title_el.text.strip()
    except Exception:
        pass

    # short description / tagline
    for sel in ["p#app-tagline", ".app-tagline", ".small.tagline", "meta[name='description']"]:
        els = driver.find_elements(By.CSS_SELECTOR, sel)
        if els:
            if sel.startswith("meta"):
                content = els[0].get_attribute("content") or ""
                if content.strip():
                    d["short_description"] = content.strip()
            else:
                txt = els[0].text.strip()
                if len(txt) >= 5:
                    d["short_description"] = txt
            if d["short_description"]:
                break
    # long description extraction
    long_desc = extract_section_text(driver, ("what it does", "what it does:", "what does it do"))
    if not long_desc:
        for sel in ["#app-details-left .large-12 p", ".app-details .content p", ".gallery p"]:
            paras = driver.find_elements(By.CSS_SELECTOR, sel)
            if paras:
                joined = " ".join([p.text.strip() for p in paras[:8] if p.text.strip()])
                if joined:
                    long_desc = joined
                    break

    d["long_description"] = long_desc
    d["tags"] = extract_built_with(driver)

    # Created/submitted date
    try:
        time_el = driver.find_element(By.CSS_SELECTOR, "time, .submitted-at time")
        dt = time_el.get_attribute("datetime") or time_el.text
        if dt:
            d["created_at"] = dt.strip()
    except NoSuchElementException:
        try:
            meta = driver.find_element(By.CSS_SELECTOR, "meta[property='article:published_time']")
            c = meta.get_attribute("content")
            if c:
                d["created_at"] = c.strip()
        except NoSuchElementException:
            pass

    # normalize empty strings
    for k, v in list(d.items()):
        if isinstance(v, str) and not v.strip():
            d[k] = None

    return d


def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape Devpost featured search into JSON (single-file script)")
    ap.add_argument("--pages", type=int, default=24, help="Max listing pages to crawl (default 24)")
    ap.add_argument("--listing-url", type=str, default="https://devpost.com/software/search?query=is%3Afeatured", help="Listing URL to crawl")
    ap.add_argument("--out", type=str, default="devpost_dump.json", help="Output JSON file")
    ap.add_argument("--no-headless", action="store_true", help="Run browser with UI")
    ap.add_argument("--limit", type=int, default=None, help="Limit number of project pages to scrape (after collecting links)")
    args = ap.parse_args()

    driver = setup_driver(headless=not args.no_headless)
    try:
        links = collect_project_links(driver, pages=args.pages, listing_url=args.listing_url)
        if args.limit:
            links = links[: args.limit]

        print(f"Scraping {len(links)} project pages…")
        results = []
        for i, u in enumerate(links, 1):
            try:
                item = scrape_project(driver, u)
                item.setdefault("source", "Devpost")
                item.setdefault("status", "Active")
                item["ingested_at"] = datetime.utcnow().isoformat()
                results.append(item)
                print(f"[{i}/{len(links)}] scraped: {item.get('name') or u}")
            except Exception as e:
                print(f"[warn] failed {u}: {e}")
            p_sleep()

    finally:
        try:
            driver.quit()
        except Exception:
            pass

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Wrote {len(results)} records to {args.out}")


if __name__ == "__main__":
    main()