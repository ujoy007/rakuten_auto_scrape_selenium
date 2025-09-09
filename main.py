# main.py
import time
from fastapi import FastAPI, Query
from scraper import scrape_rakuten_discounts, load_data

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Rakuten Discounts Scraper API"}

@app.get("/scrape")
def run_scraper(interval: int = Query(default=0, description="Interval in seconds (0 = run once)")):
    """
    Run scraper immediately.
    If interval > 0, it will scrape repeatedly every X seconds.
    Example: /scrape?interval=120  → scrape every 2 mins
    """
    results = []

    if interval > 0:
        # Repeat until stopped (Ctrl+C in server)
        while True:
            data = scrape_rakuten_discounts()
            results = data
            print(f"⏳ Waiting {interval} seconds before next scrape...")
            time.sleep(interval)
    else:
        results = scrape_rakuten_discounts()

    return {"status": "success", "count": len(results), "data": results}

@app.get("/data")
def get_data():
    data = load_data()
    return {"count": len(data), "data": data}
