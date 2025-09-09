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

1. **Run the AI scraper:**

   ```bash
   python ai_scraper.py
   ```

   This will scrape the Rakuten page, perform OCR, index content with embeddings, and save categorized results to `ai_storage.json`.

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
- `ai_scraper.py`: AI-powered scraping with OCR and embeddings using Playwright.
- `main.py`: FastAPI application with endpoints.
- `start_server.py`: Script to start the FastAPI server.
- `storage.json`: JSON file where traditional scraped data is stored.
- `ai_storage.json`: JSON file where AI-scraped and categorized data is stored.
- `requirements.txt`: List of Python dependencies.

## Notes

- The scrapers use headless Chrome for automation.
- Data is appended to existing data in `storage.json` and `ai_storage.json` on each scrape.
- Translation may fail if Google Translate is unavailable; in such cases, original Japanese text is kept.
- Ensure Chrome and Tesseract OCR are installed and up-to-date for best compatibility.
- The AI scraper requires downloading embedding models on first run.

## License

This project is for educational purposes. Please respect Rakuten's terms of service when scraping.