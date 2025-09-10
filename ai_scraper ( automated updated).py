# ai_scraper.py
# Rakuten Super Sale scraper with banners + products
# - Safe parsing (no NoneType errors)
# - Deduplication across runs
# - Monitoring with stop-after-X-rounds
# - Network blocking for faster loading
# - Discount label translation JA→EN
# - Symbol cleanup in product titles

import time
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError
from deep_translator import GoogleTranslator
from functools import lru_cache

# ----------------------------
# Setup
# ----------------------------
DATA_FILE = Path("ai_storage.json")
translator = GoogleTranslator(source="ja", target="en")

# ----------------------------
# Helpers
# ----------------------------
@lru_cache(maxsize=1000)
def translate_to_en(text: str) -> str:
    if not text:
        return ""
    try:
        return translator.translate(text.strip())
    except Exception:
        return text.strip()

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def clean_text(text: str) -> str:
    """Remove extra spaces and unwanted symbols."""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[＼♪★☆！!／]+", "", text)  # remove decorative chars
    return text.strip()

def block_unwanted(route, request):
    """Block ads, trackers, analytics for faster load"""
    unwanted = ["doubleclick", "googletagmanager", "analytics", "facebook", "adservice", "scorecardresearch"]
    if any(domain in request.url for domain in unwanted):
        return route.abort()
    return route.continue_()

# ----------------------------
# Banner Extraction
# ----------------------------
def extract_banner_texts(page, known_banners: set, max_banners: int = 20):
    banners = []
    duplicates_banners = 0
    img_selectors = "img[src*='banner'], img[src*='sale'], img[alt*='割引'], img[alt*='セール'], img[class*='banner']"
    img_elements = page.locator(img_selectors).all()

    print(f"🔎 Found {len(img_elements)} potential banner images")
    for img in img_elements[:max_banners]:
        src = img.get_attribute("src")
        alt = img.get_attribute("alt") or ""
        title = img.get_attribute("title") or ""
        text_ja = clean_text(alt or title)

        if not text_ja:
            continue

        key = (src, text_ja)
        if key in known_banners:
            duplicates_banners += 1
            continue

        banners.append({
            "text_ja": text_ja,
            "text_en": translate_to_en(text_ja),
            "image_url": src,
            "scraped_at": timestamp()
        })
        known_banners.add(key)

    print(f"🖼️ Extracted {len(banners)} new banner texts (skipped {duplicates_banners} duplicates)")
    return banners, known_banners, duplicates_banners

# ----------------------------
# Product Scraping
# ----------------------------
def scrape_products(url: str, user_limit: int, known_links: set, known_banners: set, max_retries: int = 2):
    print(f"🌐 Visiting: {url}")
    products, banners = [], []
    duplicates_products = 0
    duplicates_banners = 0
    total_cards = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        context.route("**/*", block_unwanted)  # 🚫 block trackers
        page = context.new_page()

        for attempt in range(max_retries):
            try:
                print(f"📡 Attempt {attempt + 1}/{max_retries} to load page")
                page.goto(url, timeout=60000, wait_until="domcontentloaded")
                page.wait_for_selector("div.ecm-ad", timeout=15000)
                print("✅ Product containers detected")

                # Scroll down to load more
                last_height = page.evaluate("document.body.scrollHeight")
                for _ in range(10):
                    page.mouse.wheel(0, 1500)
                    page.wait_for_timeout(500)
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                print("✅ Page fully loaded")

                # Banners
                new_banners, known_banners, duplicates_banners = extract_banner_texts(page, known_banners)
                banners.extend(new_banners)

                # Products
                cards = page.query_selector_all("div.ecm-ad")
                total_cards = len(cards)
                print(f"🔎 Found {total_cards} product cards")
                print(f"📦 Scraping {user_limit} products out of {total_cards}")

                count = 0
                for card in cards:
                    if count >= user_limit:
                        break
                    try:
                        link_el = card.query_selector("a.ecm-ad-link")
                        img_el = card.query_selector("img")
                        title_el = card.query_selector(".ecm-ad-name")
                        orig_el = card.query_selector(".ecm-ad-price-original")
                        disc_el = card.query_selector(".ecm-ad-price-amount")
                        label_el = card.query_selector(".ecm-ad-label")

                        if not link_el or not img_el or not disc_el:
                            continue  # skip invalid cards safely

                        link = link_el.get_attribute("href")
                        image_url = img_el.get_attribute("src")
                        title_ja = clean_text(title_el.inner_text() if title_el else "")
                        original_price = clean_text(orig_el.inner_text()) if orig_el else None
                        discounted_price = clean_text(disc_el.inner_text()) if disc_el else None
                        discount_percent_ja = clean_text(label_el.inner_text()) if label_el else None
                        discount_percent_en = translate_to_en(discount_percent_ja) if discount_percent_ja else None

                        if not link or link in known_links or not discounted_price:
                            duplicates_products += 1
                            continue

                        products.append({
                            "title_ja": title_ja,
                            "title_en": translate_to_en(title_ja),
                            "original_price": original_price,
                            "discounted_price": discounted_price,
                            "discount_percent_ja": discount_percent_ja,
                            "discount_percent_en": discount_percent_en,
                            "image_url": image_url,
                            "link": link,
                            "scraped_at": timestamp()
                        })
                        known_links.add(link)
                        count += 1

                        if count % 5 == 0:
                            print(f"✅ Collected {count} products so far...")

                    except Exception as e:
                        print(f"⚠️ Error parsing product: {e}")
                        continue

                break
            except TimeoutError:
                print(f"⏳ Timeout on attempt {attempt + 1}, retrying in 5s...")
                time.sleep(5)  # delay before retry
                if attempt == max_retries - 1:
                    print("❌ Max retries reached")

        context.close()
        browser.close()

    print(
        f"✅ Round summary: {len(products)} new products, {len(banners)} new banners "
        f"(skipped {duplicates_products} duplicate products, {duplicates_banners} duplicate banners)"
    )
    return {"products": products, "banners": banners, "total_found": total_cards}, known_links, known_banners

# ----------------------------
# Save to JSON (deduplicated)
# ----------------------------
def load_existing_json(filename=DATA_FILE):
    if not filename.exists():
        return {"products": [], "banners": []}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {"products": [], "banners": []}
            return json.loads(content)
    except Exception:
        return {"products": [], "banners": []}

def save_to_json(data, filename=DATA_FILE):
    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        existing = load_existing_json(filename)

        existing_links = {p["link"] for p in existing["products"]}
        new_products = [p for p in data["products"] if p["link"] not in existing_links]

        existing_banners = {(b["image_url"], b["text_ja"]) for b in existing["banners"]}
        new_banners = [b for b in data["banners"] if (b["image_url"], b["text_ja"]) not in existing_banners]

        existing["products"].extend(new_products)
        existing["banners"].extend(new_banners)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved {len(new_products)} new products and {len(new_banners)} new banners to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    url = "https://event.rakuten.co.jp/campaign/supersale/?l-id=top_normal_emergency_pc_big01"
    known_links = set()
    known_banners = set()

    # First detect product count
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        context.route("**/*", block_unwanted)  # 🚫 block trackers
        page = context.new_page()
        page.goto(url, timeout=60000, wait_until="domcontentloaded")
        page.wait_for_selector("div.ecm-ad", timeout=15000)
        total_cards = len(page.query_selector_all("div.ecm-ad"))
        context.close()
        browser.close()

    print(f"\n🔎 Detected {total_cards} product cards on the page.")
    user_limit = int(input(f"👉 How many products do you want to scrape? (max {total_cards}): "))

    results, known_links, known_banners = scrape_products(url, user_limit, known_links, known_banners)
    if results:
        save_to_json(results)
        print("\n📊 Sample Output:")
        print(json.dumps(results, indent=2, ensure_ascii=False)[:2000])

    repeat = input("\n🔄 Do you want to check again for new discounts automatically? (y/n): ").strip().lower()
    if repeat == "y":
        interval_raw = input("⏱️ Enter interval (e.g., '60' for 60 sec or '5m' for 5 minutes): ").strip()
        interval = int(interval_raw[:-1]) * 60 if interval_raw.endswith("m") else int(interval_raw)
        max_rounds = int(input("🔢 How many rounds should I run? (0 = infinite): ").strip())
        round_count = 0

        print(f"🔁 Monitoring mode ON — checking every {interval} seconds. Stop after {max_rounds if max_rounds else '∞'} rounds.\n")

        while True:
            time.sleep(interval)
            round_count += 1
            print(f"\n🔄 Round {round_count} starting at {timestamp()} ...")
            results, known_links, known_banners = scrape_products(url, user_limit, known_links, known_banners)
            if results and (results["products"] or results["banners"]):
                save_to_json(results)
            else:
                print("✅ No new products/banners found this round.")

            if max_rounds > 0 and round_count >= max_rounds:
                print(f"🛑 Stopping after {round_count} rounds.")
                break
