# AI-Powered Website Data Scraping

This project scrapes discounted items from Rakuten's Super Sale page using Selenium and Playwright, translates Japanese text to English, performs OCR on images, and uses AI embeddings for semantic search. It also provides a FastAPI API to run the scraper and retrieve data.

## Features

- Scrapes product titles, prices, discounts, images, and links from Rakuten Super Sale using Selenium.
- AI-powered scraping with Playwright, OCR for images, and semantic search using embeddings.
- Translates Japanese text to English using Google Translate.
- Saves structured data to `storage.json` and AI results to `ai_storage.json`.
- FastAPI server for API endpoints to trigger scraping and retrieve data.
- Supports repeated scraping with intervals.

## Requirements

- Python 3.8 or higher
- Google Chrome browser (for Selenium and Playwright)
- Tesseract OCR installed (for image text extraction)
- Dependencies: `selenium`, `googletrans`, `fastapi`, `uvicorn`, `playwright`, `sentence-transformers`, `chromadb`, `requests`, `pillow`, `pytesseract`

Install dependencies:

```bash
pip install -r requirements.txt
```

You may also need to install ChromeDriver, but Selenium can handle it automatically with `webdriver-manager`.

## Usage

### AI Scraper (Automated Updated Version)

The `ai_scraper ( automated updated).py` script is an advanced scraper for Rakuten Super Sale that extracts products and banners, translates Japanese text to English, and supports automated monitoring for new discounts.

**Features:**
- Scrapes product details: titles (Japanese/English), prices, discounts, images, and links.
- Extracts banner texts and images with translation.
- Deduplicates data across runs to avoid repeats.
- Blocks unwanted network requests (ads, trackers) for faster loading.
- Safe parsing to handle missing elements without errors.
- Automated monitoring mode with customizable intervals and round limits.
- Saves data to `ai_storage.json` in JSON format.

**How to Run:**

1. **Interactive Scraping:**

    ```bash
    python "ai_scraper ( automated updated).py"
    ```

    - The script will detect the number of available products on the page.
    - It will prompt you to enter how many products to scrape (e.g., 10, 50).
    - It scrapes the specified number of products and banners, translates text, and saves to `ai_storage.json`.
    - After the initial scrape, it offers to enter automated monitoring mode.

2. **Automated Monitoring Mode:**

    - If you choose 'y' when prompted, enter:
      - Interval: Time between checks (e.g., '60' for 60 seconds, '5m' for 5 minutes).
      - Max rounds: Number of rounds to run (0 for infinite).
    - The script will repeatedly scrape at the set interval, only saving new data.
    - It stops after the specified rounds or manually.

**Sample Output:**
The scraped data includes:
- Products: `title_ja`, `title_en`, `original_price`, `discounted_price`, `discount_percent_ja`, `discount_percent_en`, `image_url`, `link`, `scraped_at`.
- Banners: `text_ja`, `text_en`, `image_url`, `scraped_at`.

Data is appended to `ai_storage.json` with deduplication.

### Traditional Scraper (FastAPI Server)

2. **Start the server for traditional scraping:**

    ```bash
    python start_server.py
    ```

    The server will run on `http://127.0.0.1:8000`.

3. **Scrape data immediately:**

    - Endpoint: `GET /scrape`
    - Example: `http://127.0.0.1:8000/scrape`

4. **Scrape data repeatedly with interval:**

    - Endpoint: `GET /scrape?interval=<seconds>`
    - Example: `http://127.0.0.1:8000/scrape?interval=120` (scrapes every 2 minutes)

5. **Retrieve stored data:**

    - Endpoint: `GET /data`
    - Returns all scraped items from `storage.json`.

## Files

- `scraper.py`: Traditional scraping logic using Selenium.
- `ai_scraper.py`: Basic AI-powered scraping script.
- `ai_scraper ( automated updated).py`: Advanced scraper with product/banner extraction, Japanese-to-English translation, deduplication, automated monitoring, and network optimization using Playwright.
- `main.py`: FastAPI application with endpoints.
- `start_server.py`: Script to start the FastAPI server.
- `storage.json`: JSON file where traditional scraped data is stored.
- `ai_storage.json`: JSON file where AI-scraped data (products and banners) is stored with deduplication.
- `requirements.txt`: List of Python dependencies.

## Detailed Python Files Description

The project contains several Python scripts that have evolved over time, each building on the previous versions with added features. Below is a sequential overview of the Python files, organized by development progression:

### 1. `scraper.py`
- **Purpose**: Basic web scraper for Rakuten Super Sale using Selenium.
- **Features**:
  - Extracts product titles, original/discounted prices, discount labels, images, and links.
  - Translates Japanese text to English using Google Translate.
  - Auto-scrolls to load lazy content.
  - Saves data to `storage.json`, appending new items to existing data.
- **Usage**: Run directly or via the FastAPI server in `main.py`.
- **Limitations**: No deduplication, no OCR, no automated monitoring.

### 2. `main.py`
- **Purpose**: FastAPI web server that integrates with `scraper.py` for API-based scraping.
- **Features**:
  - Provides REST API endpoints: `/scrape` (with optional interval for repeated scraping) and `/data` (to retrieve stored data).
  - Supports one-time or continuous scraping with customizable intervals.
- **Usage**: Start the server with `python main.py`, then access via browser or API calls.
- **Dependencies**: Requires `scraper.py` for scraping functionality.

### 3. `ai_scraper (old).py`
- **Purpose**: Early AI-powered scraper using Playwright, OCR, and semantic search.
- **Features**:
  - Scrapes visible text and performs OCR on images using Tesseract.
  - Filters content based on discount-related keywords.
  - Uses sentence transformers for embeddings and ChromaDB for semantic search and storage.
  - Categorizes scraped data into discounts, prices, coupons, etc.
- **Usage**: Run directly to scrape and index content for querying.
- **Limitations**: No product-specific extraction, focuses on general text snippets.

### 4. `ai_scraper (scapy based).py`
- **Purpose**: Advanced AI scraper with NLP and concurrent processing.
- **Features**:
  - Uses Playwright for scraping, OCR for banner images, and spaCy for NLP-based product detection.
  - Concurrent OCR processing with ThreadPoolExecutor.
  - Parses prices and calculates discount percentages.
  - Translates Japanese text to English.
  - Saves structured data to `ai_storage.json`.
- **Usage**: Run directly for one-time scraping.
- **Note**: This appears to be an intermediate version; `ai_scraper.py` is a duplicate.

### 5. `ai_scraper.py`
- **Purpose**: Duplicate of `ai_scraper (scapy based).py`.
- **Note**: Identical functionality to the scapy-based version. Consider consolidating.

### 6. `ai_scraper ( automated updated).py`
- **Purpose**: Latest and most advanced scraper with automated monitoring.
- **Features**:
  - Extracts both products and banners with deduplication across runs.
  - Translates Japanese text to English and cleans symbols.
  - Blocks unwanted network requests for faster loading.
  - Interactive mode: Prompts user for number of products to scrape.
  - Automated monitoring mode: Repeated scraping at set intervals with configurable rounds.
  - Safe parsing to handle missing elements without errors.
  - Saves to `ai_storage.json` with deduplication.
- **Usage**: Run directly; choose between interactive or automated mode.
- **Advantages**: Most feature-complete, includes monitoring and optimization.

## Notes

- The scrapers use headless Chrome for automation.
- Data is appended to existing data in `storage.json` and `ai_storage.json` on each scrape.
- Translation may fail if Google Translate is unavailable; in such cases, original Japanese text is kept.
- Ensure Chrome and Tesseract OCR are installed and up-to-date for best compatibility.
- The AI scraper requires downloading embedding models on first run.

## License

This project is for educational purposes. Please respect Rakuten's terms of service when scraping.