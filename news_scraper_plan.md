# News Scraper - Implementation Plan

**Task**: Build a news scraper that collects headlines, URLs, and timestamps from Reuters and AP News.

**Context**: This is a learning project that will eventually integrate with a Polymarket whale tracker. For now, just focus on reliably scraping and storing articles. User is on Mac for local testing, will deploy to DigitalOcean later.

## Tech Stack

- Python 3
- requests
- beautifulsoup4
- SQLite

## File Structure

```
news_scraper/
├── scraper.py          # Main script - fetches and stores articles
├── db.py               # Database setup and queries
├── sources/
│   ├── __init__.py
│   ├── reuters.py      # Reuters-specific parsing
│   └── ap.py           # AP-specific parsing
├── requirements.txt
└── README.md
```

## Database Schema

```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    published_at TEXT,
    scraped_at TEXT NOT NULL
);
```

## Implementation Steps

1. Create project structure and `requirements.txt` (requests, beautifulsoup4)

2. Build `db.py` with schema init, insert function (handle duplicates gracefully via URL unique constraint), and a simple query function to view recent articles

3. Build `sources/reuters.py` - fetch https://www.reuters.com/world/ and/or other sections, inspect the HTML to find working selectors for article titles and URLs, extract what's available, return list of dicts with keys: source, url, title, published_at (if available), scraped_at

4. Build `sources/ap.py` - same approach for https://apnews.com, different selectors

5. Build `scraper.py` - import both sources, run them, insert results to DB, print summary of what was found/added. Add 1-2 second delays between requests.

6. Add error handling - if a source fails, log it and continue with other sources. Don't crash the whole script.

7. Write README with: setup instructions (venv, pip install), how to run manually, how to set up cron for Mac (`*/10 * * * * cd /path/to/news_scraper && ./venv/bin/python scraper.py >> scrape.log 2>&1`), and notes about deploying to DigitalOcean

## Important Notes

- The HTML selectors WILL require trial and error. Fetch the actual pages, inspect the HTML, find what works. Common patterns: `article` tags, `h2`/`h3` for headlines, `a[href*="/article/"]` or similar for links.
- If timestamps aren't easily available in list views, that's fine - just use scraped_at. Don't over-engineer it.
- Fail gracefully. Log errors. Don't crash on one bad source.
- Test that it actually works by running it and checking the database.

## Out of Scope (for now)

- JavaScript rendering (would need Selenium/Playwright)
- Paywalled content
- Full article text extraction
- Keyword matching (comes later)

## Future Plans

- Add more sources: BBC, NPR, Bloomberg, crypto-specific sites
- Keyword matching against Polymarket markets
- Cross-reference with whale trades database
- Alerting (Discord/Telegram) on matches
- RSS feeds as fallback for flaky HTML scraping
