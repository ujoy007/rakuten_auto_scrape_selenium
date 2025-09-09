##..................playwright version.......##

# # scraper.py
# import json
# import traceback
# from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# DATA_FILE = "storage.json"

# def scrape_rakuten_discounts():
#     """
#     Scrape discounted items from Rakuten's Super Sale page.
#     Extracts product title, prices, discount label, image, and link.
#     """
#     items = []
#     try:
#         with sync_playwright() as p:
#             browser = p.chromium.launch(headless=True)
#             context = browser.new_context(
#                 user_agent=(
#                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
#                     "AppleWebKit/537.36 (KHTML, like Gecko) "
#                     "Chrome/116.0.0.0 Safari/537.36"
#                 )
#             )
#             page = context.new_page()

#             print("➡️ Navigating to Rakuten Super Sale page...")
#             page.goto(
#                 "https://event.rakuten.co.jp/campaign/supersale/?l-id=top_normal_emergency_pc_big01",
#                 timeout=30000
#             )

#             try:
#                 # Wait until product ads are visible
#                 page.wait_for_selector("div.ecm-ad", timeout=10000)
#             except PlaywrightTimeoutError:
#                 print("⚠️ Timeout: No products found within 10s")
#                 browser.close()
#                 return []

#             print("✅ Page loaded. Extracting items...")

#             # Use Rakuten's product container selector
#             product_blocks = page.query_selector_all("div.ecm-ad")

#             for block in product_blocks:
#                 try:
#                     # Product title
#                     title_el = block.query_selector(".ecm-ad-name")
#                     title = title_el.inner_text().strip() if title_el else "No title"

#                     # Prices
#                     original_price_el = block.query_selector(".ecm-ad-price-original")
#                     discounted_price_el = block.query_selector(".ecm-ad-price-amount")

#                     original_price = original_price_el.inner_text().strip() if original_price_el else None
#                     discounted_price = discounted_price_el.inner_text().strip() if discounted_price_el else None

#                     # Discount label (e.g., 半額以下, 50%OFF)
#                     label_el = block.query_selector(".ecm-ad-label")
#                     discount_label = label_el.inner_text().strip() if label_el else None

#                     # Image
#                     img_el = block.query_selector("img")
#                     image_url = img_el.get_attribute("src") if img_el else None

#                     # Product link
#                     link_el = block.query_selector("a.ecm-ad-link")
#                     link_url = link_el.get_attribute("href") if link_el else None

#                     if original_price and discounted_price:
#                         items.append({
#                             "title": title,
#                             "original_price": original_price,
#                             "discounted_price": discounted_price,
#                             "discount_label": discount_label,
#                             "image_url": image_url,
#                             "link": link_url,
#                         })

#                 except Exception as inner_e:
#                     print(f"⚠️ Error parsing block: {inner_e}")

#             browser.close()

#         # Save results into JSON
#         with open(DATA_FILE, "w", encoding="utf-8") as f:
#             json.dump(items, f, indent=4, ensure_ascii=False)

#     except Exception as e:
#         print("❌ Error during scraping:")
#         traceback.print_exc()   # full error stack
#         return []

#     print(f"✅ Scraping finished. Found {len(items)} items.")
#     return items


# def load_data():
#     """Load previously scraped data from storage.json."""
#     try:
#         with open(DATA_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return []

#..........selenium version...........##

# scraper.py

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from googletrans import Translator

DATA_FILE = "storage.json"
translator = Translator()

def translate_text(text: str) -> str:
    """Translate Japanese text to English using Google Translate."""
    if not text:
        return text
    try:
        result = translator.translate(text, src="ja", dest="en")
        return result.text
    except Exception:
        return text  # fallback to original if translation fails

def scrape_rakuten_discounts():
    """
    Scrape discounted items from Rakuten's Super Sale page using Selenium.
    Extracts product title, original price, discounted price, 
    discount label, image URL, and product link.
    Translates Japanese text to English automatically.
    """
    items = []
    try:
        # Setup Chrome options
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/116.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=options)

        print("➡️ Navigating to Rakuten Super Sale page...")
        driver.get("https://event.rakuten.co.jp/campaign/supersale/?l-id=top_normal_emergency_pc_big01")

        time.sleep(5)  # wait for page load

        # Auto-scroll to load lazy content
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 2000);")
            time.sleep(2)

        print("✅ Page loaded. Extracting items...")

        product_blocks = driver.find_elements(By.CSS_SELECTOR, "div.ecm-ad")

        for block in product_blocks:
            try:
                # Title
                try:
                    title = block.find_element(By.CSS_SELECTOR, ".ecm-ad-name").text.strip()
                except NoSuchElementException:
                    title = "No title"

                # Prices
                try:
                    original_price = block.find_element(By.CSS_SELECTOR, ".ecm-ad-price-original").text.strip()
                except NoSuchElementException:
                    original_price = None

                try:
                    discounted_price = block.find_element(By.CSS_SELECTOR, ".ecm-ad-price-amount").text.strip()
                except NoSuchElementException:
                    discounted_price = None

                # Discount label
                try:
                    discount_label = block.find_element(By.CSS_SELECTOR, ".ecm-ad-label").text.strip()
                except NoSuchElementException:
                    discount_label = None

                # Image URL
                try:
                    image_url = block.find_element(By.TAG_NAME, "img").get_attribute("src")
                except NoSuchElementException:
                    image_url = None

                # Product link
                try:
                    link_url = block.find_element(By.CSS_SELECTOR, "a.ecm-ad-link").get_attribute("href")
                except NoSuchElementException:
                    link_url = None

                if original_price and discounted_price:
                    items.append({
                        "title_ja": title,
                        "title_en": translate_text(title),
                        "original_price": original_price,
                        "discounted_price": discounted_price,
                        "discount_label_ja": discount_label,
                        "discount_label_en": translate_text(discount_label),
                        "image_url": image_url,
                        "link": link_url,
                    })

            except Exception as inner_e:
                print(f"⚠️ Error parsing block: {inner_e}")

        driver.quit()

        # 🔹 Load old data first
        existing_data = load_data()

        # 🔹 Add new items to the old list
        all_items = existing_data + items

        # 🔹 Save everything back
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(all_items, f, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return []

    print(f"✅ Scraping finished. Found {len(items)} items.")
    return items


def load_data():
    """Load previously scraped data from storage.json."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    




