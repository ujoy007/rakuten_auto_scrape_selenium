# ai_scraper.py (Rakuten Super Sale scraper with OCR + structured JSON)

import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import io
from PIL import Image
import pytesseract

# ----------------------------
# Setup Embeddings & Storage
# ----------------------------
print("🚀 Loading embeddings model (paraphrase-MiniLM-L3-v2)...")
model = SentenceTransformer("sentence-transformers/paraphrase-MiniLM-L3-v2")
print("✅ Embeddings model loaded!")

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("rakuten_content")

DATA_FILE = Path("ai_storage.json")

# ----------------------------
# OCR for Images
# ----------------------------
def extract_text_from_images(page):
    """Download and OCR all images on the page"""
    img_elements = page.locator("img").all()
    ocr_texts = []

    for img in img_elements:
        try:
            src = img.get_attribute("src")
            if not src or not src.startswith("http"):
                continue

            response = requests.get(src, timeout=10)
            if response.status_code != 200:
                continue

            img_data = Image.open(io.BytesIO(response.content)).convert("RGB")

            # OCR with Tesseract (Japanese + English)
            text = pytesseract.image_to_string(img_data, lang="jpn+eng").strip()

            if text:
                ocr_texts.append(text)

        except Exception:
            continue

    print(f"🖼️ OCR extracted {len(ocr_texts)} snippets from images")
    return ocr_texts


# ----------------------------
# Scraping Function
# ----------------------------
def scrape_page(url: str):
    """Scrape and filter visible + OCR text from a web page"""
    print(f"🌐 Visiting page: {url}")
    texts = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded", timeout=15000)

            # 🔄 Scroll to bottom to trigger lazy loading
            page.evaluate(
                """() => {
                    return new Promise(resolve => {
                        let totalHeight = 0;
                        let distance = 500;
                        let timer = setInterval(() => {
                            window.scrollBy(0, distance);
                            totalHeight += distance;

                            if (totalHeight >= document.body.scrollHeight) {
                                clearInterval(timer);
                                resolve();
                            }
                        }, 400);
                    });
                }"""
            )
            time.sleep(3)  # allow lazy-loaded content

            print("✅ Finished scrolling page")

            # Grab raw text
            raw_texts = page.locator("body *").all_text_contents()
            print(f"🔎 Raw snippets found: {len(raw_texts)}")

            # Expanded keyword set
            keywords = [
                "%", "OFF", "割引", "セール", "円", "引き",
                "半額", "タイムセール", "キャンペーン", "ポイント"
            ]

            # Filter texts
            texts = [
                t.strip()
                for t in raw_texts
                if t.strip()
                and len(t.strip()) < 80
                and any(k in t for k in keywords)
            ]

            # OCR text from images
            ocr_texts = extract_text_from_images(page)
            texts.extend(ocr_texts)

            # Split long blocks into smaller snippets
            split_texts = []
            for t in texts:
                if "\n" in t:
                    split_texts.extend([part.strip() for part in t.split("\n") if part.strip()])
                else:
                    split_texts.append(t)

            # Deduplicate
            texts = list(set(split_texts))

            print(f"✅ Filtered {len(texts)} useful snippets")

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

        finally:
            browser.close()

    return texts


# ----------------------------
# Indexing (store in Chroma)
# ----------------------------
def index_page(url: str):
    """Scrape + embed filtered page content into ChromaDB"""
    texts = scrape_page(url)

    if not texts:
        print("⚠️ No useful text found, skipping indexing")
        return 0

    print("🧩 Encoding & indexing into ChromaDB...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True).tolist()
    ids = [f"{url}_{i}" for i in range(len(texts))]

    collection.add(documents=texts, embeddings=embeddings, ids=ids)

    print(f"✅ Indexed {len(texts)} snippets from {url}")
    return len(texts)


# ----------------------------
# Querying
# ----------------------------
def query_page(query: str, top_k: int = 10):
    """Search page embeddings semantically"""
    print(f"🔎 Searching for: '{query}'")
    emb = model.encode(query).tolist()
    results = collection.query(query_embeddings=[emb], n_results=top_k)
    return results.get("documents", [[]])[0]


# ----------------------------
# Save results to JSON
# ----------------------------
def save_to_json(data, filename=DATA_FILE):
    if filename.exists():
        try:
            with open(filename, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except json.JSONDecodeError:
            existing = []
    else:
        existing = []

    existing.append(data)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)

    print(f"💾 Results saved to {filename}")


# ----------------------------
# Main Run
# ----------------------------
if __name__ == "__main__":
    url = "https://event.rakuten.co.jp/campaign/supersale/?l-id=top_normal_emergency_pc_big01"

    count = index_page(url)
    if count == 0:
        exit()

    # Category mapping
    category_queries = {
        "discounts": ["discount", "割引", "off", "OFF", "引き", "半額"],
        "prices": ["price", "円"],
        "coupons": ["クーポン", "coupon"],
        "points": ["ポイント"],
        "time_sales": ["セール", "タイムセール", "campaign", "キャンペーン"],
    }

    results = {}
    for category, queries in category_queries.items():
        collected = []
        for q in queries:
            matches = query_page(q, top_k=10)
            collected.extend(matches)
        results[category] = list(set(collected))  # dedupe

    save_to_json({"url": url, "results": results})

    print("\n📊 Final structured results:")
    for cat, vals in results.items():
        print(f"{cat.upper()} 👉 {vals[:10]}")
