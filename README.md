# Basic Website Data Scraping

This project scrapes discounted items from Rakuten's Super Sale page using Selenium, translates Japanese text to English, and provides a FastAPI API to run the scraper and retrieve data.

## Features

- Scrapes product titles, prices, discounts, images, and links from Rakuten Super Sale.
- Translates Japanese text to English using Google Translate.
- Saves data to `storage.json`.
- FastAPI server for API endpoints to trigger scraping and retrieve data.
- Supports repeated scraping with intervals.

## Requirements

- Python 3.8 or higher
- Google Chrome browser (for Selenium WebDriver)
- Dependencies: `selenium`, `googletrans`, `fastapi`, `uvicorn`

Install dependencies:

```bash
pip install selenium googletrans==4.0.0rc1 fastapi uvicorn
```

You may also need to install ChromeDriver, but Selenium can handle it automatically with `webdriver-manager`.

## Usage

1. **Start the server:**

   ```bash
   python start_server.py
   ```

   The server will run on `http://127.0.0.1:8000`.

2. **Scrape data immediately:**

   - Endpoint: `GET /scrape`
   - Example: `http://127.0.0.1:8000/scrape`

3. **Scrape data repeatedly with interval:**

   - Endpoint: `GET /scrape?interval=<seconds>`
   - Example: `http://127.0.0.1:8000/scrape?interval=120` (scrapes every 2 minutes)

4. **Retrieve stored data:**

   - Endpoint: `GET /data`
   - Returns all scraped items from `storage.json`.

## Files

- `scraper.py`: Contains the main scraping logic using Selenium.
- `main.py`: FastAPI application with endpoints.
- `start_server.py`: Script to start the FastAPI server.
- `storage.json`: JSON file where scraped data is stored.
- `requirements.txt`: (Currently empty) List of Python dependencies.

## Notes

- The scraper uses headless Chrome for automation.
- Data is appended to existing data in `storage.json` on each scrape.
- Translation may fail if Google Translate is unavailable; in such cases, original Japanese text is kept.
- Ensure Chrome is installed and up-to-date for best compatibility.

## License

This project is for educational purposes. Please respect Rakuten's terms of service when scraping.