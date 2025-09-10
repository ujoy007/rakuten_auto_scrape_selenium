# ai_scraper.py
# AI-powered scraper for Rakuten Super Sale
# - Uses Playwright for scraping
# - OCR (pytesseract) for banner images
# - NLP (spaCy) for smarter product detection
# - GoogleTranslator for JA→EN

import time
import json
import re
import io
import requests
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
from PIL import Image
import pytesseract
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
import spacy

# ----------------------------
# Setup
# ----------------------------
DATA_FILE = Path("ai_storage.json")
translator = GoogleTranslator(source="ja", target="en")

# NLP models
try:
    nlp_en = spacy.load("en_core_web_sm")
except:
    nlp_en = spacy.blank("en")

nlp_ja = spacy.blank("ja")  # minimal Japanese tokenizer

# ----------------------------
# Helpers
# ----------------------------
@lru_cache(maxsize=1000)
def cached_translate(text: str) -> str:
    return translator.translate(text) if text else ""

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\\!/！＼／]", "", text)
    return text.strip()

def safe_get_attribute(locator, attr, default=None):
    try:
        return locator.get_attribute(attr) or default
    except Exception:
        return default

# ----------------------------
# OCR for Images
# ----------------------------
def extract_text_from_image(src: str, min_width: int = 200, min_height: int = 50):
    try:
        if src.endswith(".svg"):
            print(f"⚠️ Skipping SVG image: {src}")
            return None
        response = requests.get(src, timeout=5)
        if response.status_code != 200:
            return None

        img_data = Image.open(io.BytesIO(response.content)).convert("RGB")
        width, height = img_data.size
        if width < min_width or height < min_height:
            return None

        text = pytesseract.image_to_string(img_data, lang="jpn+eng", config="--psm 6").strip()
        if not text:
            return None

        clean_ja = clean_text(text)
        return {
            "text_ja": clean_ja,
            "text_en": cached_translate(clean_ja),
            "image_url": src
        }
    except Exception as e:
        print(f"⚠️ OCR error for {src}: {e}")
        return None

def extract_text_from_images(page, max_images: int = 20):
    img_selectors = "img[src*='banner'], img[src*='sale'], img[alt*='割引'], img[alt*='セール'], img[class*='banner']"
    img_elements = page.locator(img_selectors).all()
    banners, img_urls = [], []

    print(f"🔎 Found {len(img_elements)} potential banner images")
    for img in img_elements[:max_images]:
        src = safe_get_attribute(img, "src")
        if src and src.startswith("http"):
            img_urls.append(src)

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(extract_text_from_image, src): src for src in img_urls}
        for future in as_completed(future_to_url):
            result = future.result()
            if result:
                banners.append(result)

    print(f"🖼️ OCR extracted {len(banners)} banners")
    return banners

# ----------------------------
# Price Helpers
# ----------------------------
def parse_prices(text: str):
    prices = re.findall(r"[0-9,]+円", text)
    original_price, discounted_price, discount_percent = None, None, None

    if len(prices) >= 2:
        original_price, discounted_price = prices[0], prices[1]
    elif len(prices) == 1:
        discounted_price = prices[0]

    try:
        if original_price and discounted_price:
            op = int(original_price.replace("円", "").replace(",", ""))
            dp = int(discounted_price.replace("円", "").replace(",", ""))
            discount_percent = round((1 - dp / op) * 100) if op > 0 else None
    except:
        discount_percent = None

    return original_price, discounted_price, f"{discount_percent}%" if discount_percent else None

# ----------------------------
# NLP Smart Filtering
# ----------------------------
PRODUCT_KEYWORDS = ["円", "割引", "セール", "ポイント", "送料無料", "OFF", "%"]

def is_likely_product(text: str) -> bool:
    if not text or len(text) < 10:
        return False
    if any(kw in text for kw in PRODUCT_KEYWORDS):
        return True
    doc = nlp_ja(text)
    if len([t for t in doc if t.pos_ in ("NOUN", "PROPN")]) > 2:
        return True
    return False

# ----------------------------
# Scraping Products
# ----------------------------
def scrape_products(url: str, max_retries: int = 2, max_cards: int = 150):
    print(f"🌐 Visiting: {url}")
    products, ocr_banners = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()

        for attempt in range(max_retries):
            try:
                print(f"📡 Attempt {attempt + 1}/{max_retries} to load page")
                page.goto(url, timeout=30000)
                page.wait_for_load_state("domcontentloaded", timeout=15000)

                product_selector = "div[class*='product'], div[class*='item'], div:has(img):has-text('円')"
                page.wait_for_selector(product_selector, timeout=10000, state="visible")
                print("✅ Product containers detected")

                # Scroll to load
                last_height = page.evaluate("document.body.scrollHeight")
                for _ in range(10):
                    page.mouse.wheel(0, 1500)
                    time.sleep(0.5)
                    new_height = page.evaluate("document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height

                print("✅ Page fully loaded")

                # OCR banners
                ocr_banners = extract_text_from_images(page)

                # Product cards
                product_cards = page.locator(product_selector).all()
                print(f"🔎 Found {len(product_cards)} product cards")

                for idx, card in enumerate(product_cards[:max_cards]):
                    try:
                        link = safe_get_attribute(card.locator("a[href*='rakuten']").first, "href")
                        image_url = safe_get_attribute(card.locator("img").first, "src")

                        try:
                            text = card.evaluate("el => el.innerText") or ""
                        except Exception:
                            text = ""

                        text = text.strip()
                        if not is_likely_product(text):
                            continue
                        if not re.search(r"[0-9,]+円", text):
                            continue

                        original_price, discounted_price, discount_percent = parse_prices(text)
                        title_ja = clean_text(text.split("\n")[0][:100])
                        title_en = cached_translate(title_ja)

                        if not title_ja or not discounted_price:
                            continue

                        products.append({
                            "title_ja": title_ja,
                            "title_en": title_en,
                            "original_price": original_price,
                            "discounted_price": discounted_price,
                            "discount_percent": discount_percent,
                            "image_url": image_url,
                            "link": link,
                        })

                        if idx % 25 == 0:
                            print(f"✅ Processed {idx} cards...")

                    except Exception as e:
                        print(f"⚠️ Error processing product card {idx}: {e}")
                        continue

                break  # success, stop retries

            except TimeoutError:
                print(f"⏳ Timeout on attempt {attempt + 1}, retrying...")
                if attempt == max_retries - 1:
                    print("❌ Max retries reached")

        context.close()
        browser.close()

    print(f"✅ Extracted {len(products)} products")
    return {"products": products, "ocr_banners": ocr_banners}

# ----------------------------
# Save to JSON
# ----------------------------
def save_to_json(data, filename=DATA_FILE):
    try:
        filename.parent.mkdir(parents=True, exist_ok=True)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Saved {len(data['products'])} products and {len(data['ocr_banners'])} banners to {filename}")
    except Exception as e:
        print(f"❌ Error saving to JSON: {e}")

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    url = "https://event.rakuten.co.jp/campaign/supersale/?l-id=top_normal_emergency_pc_big01"
    start_time = time.time()
    results = scrape_products(url)
    if results:
        save_to_json(results)
        print("\n📊 Sample Output:")
        print(json.dumps(results, indent=2, ensure_ascii=False)[:2000])
    else:
        print("❌ No results to save")
    print(f"⏱️ Execution time: {time.time() - start_time:.2f} seconds")
