# AI Scraper (Automated Updated) Documentation

## Overview

This script is a powerful tool for scraping discounted products and banners from Rakuten's Super Sale page. It automatically extracts product details, translates Japanese text to English, and can run continuously to monitor for new discounts. The script is designed to be safe, efficient, and user-friendly.

## Key Features

- **Product Scraping**: Extracts product titles, prices, discounts, images, and links
- **Banner Extraction**: Collects promotional banner texts and images
- **Translation**: Automatically translates Japanese text to English
- **Deduplication**: Prevents duplicate data across multiple runs
- **Network Optimization**: Blocks ads and trackers for faster loading
- **Automated Monitoring**: Can run repeatedly at set intervals
- **Safe Parsing**: Handles missing data without crashing
- **Interactive Mode**: Asks user how many products to scrape

## Requirements

- Python 3.8 or higher
- Google Chrome browser
- Internet connection
- Required Python packages (install via `pip install -r requirements.txt`):
  - playwright
  - deep-translator
  - pathlib (built-in)

## Installation

1. Make sure you have Python installed
2. Install dependencies:
   ```bash
   pip install playwright deep-translator
   ```
3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## How to Use

### Basic Usage

1. Run the script:
   ```bash
   python "ai_scraper ( automated updated).py"
   ```

2. The script will:
   - Load the Rakuten Super Sale page
   - Count available products
   - Ask how many products you want to scrape

3. Enter the number of products (e.g., 10, 50, or the maximum available)

4. The script will scrape the data and save it to `ai_storage.json`

### Automated Monitoring Mode

After the initial scrape, the script will ask:
```
🔄 Do you want to check again for new discounts automatically? (y/n):
```

If you type `y`, it will ask for:
- **Interval**: How often to check (e.g., '60' for 60 seconds, '5m' for 5 minutes)
- **Max rounds**: How many times to run (0 = keep running forever)

Example:
- Interval: `300` (5 minutes)
- Max rounds: `10` (stop after 10 checks)

The script will then run automatically, only saving new data each time.

### Stopping the Script

- In automated mode, it will stop after the specified rounds
- You can manually stop it by pressing `Ctrl+C` in the terminal

## What Data is Collected

### Products
- **Title** (in Japanese and English)
- **Original Price**
- **Discounted Price**
- **Discount Percentage** (in Japanese and English)
- **Product Image URL**
- **Product Link**
- **Timestamp** (when scraped)

### Banners
- **Banner Text** (in Japanese and English)
- **Banner Image URL**
- **Timestamp** (when scraped)

## Output File

All data is saved to `ai_storage.json` in your project folder.

The file structure looks like this:
```json
{
  "products": [
    {
      "title_ja": "Japanese product name",
      "title_en": "English product name",
      "original_price": "¥5000",
      "discounted_price": "¥3000",
      "discount_percent_ja": "40%オフ",
      "discount_percent_en": "40% off",
      "image_url": "https://...",
      "link": "https://...",
      "scraped_at": "2025-09-10 05:41:34 UTC"
    }
  ],
  "banners": [
    {
      "text_ja": "Japanese banner text",
      "text_en": "English banner text",
      "image_url": "https://...",
      "scraped_at": "2025-09-10 05:41:34 UTC"
    }
  ]
}
```

## Tips and Troubleshooting

- **Slow Loading**: The script blocks ads/trackers to speed up loading
- **No Data Found**: Make sure the Rakuten page is accessible and has products
- **Translation Issues**: If Google Translate is unavailable, Japanese text is kept as-is
- **Duplicates**: The script automatically skips products/banners already scraped
- **Timeouts**: The script retries up to 2 times if the page takes too long to load

## Safety Notes

- This script respects Rakuten's robots.txt and terms of service
- It uses reasonable delays between requests
- Only scrapes publicly available data
- For educational and personal use only

## Technical Details

- Uses Playwright for browser automation
- Runs in headless Chrome (no visible browser window)
- Scrolls the page to load all products
- Handles network timeouts and errors gracefully
- Cleans and formats text data
- Uses caching for translation to improve speed

## Support

If you encounter issues:
1. Check that all requirements are installed
2. Ensure you have a stable internet connection
3. Verify that the Rakuten Super Sale page is accessible in your browser
4. Check the terminal output for error messages

The script provides detailed progress messages to help troubleshoot any problems.