# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All commands run from project root using the venv:

```bash
# Run scraper
./venv/bin/python3 news_scraper/scraper.py

# View recent articles
./venv/bin/python3 news_scraper/scraper.py --recent --limit 20

# Cleanup old articles (default 3 days)
./venv/bin/python3 news_scraper/scraper.py --cleanup --days 3

# Run all tests
./venv/bin/pytest tests/ -v

# Run a single test
./venv/bin/pytest tests/test_sources.py::TestBBC -v
```

## Architecture

This is a news headline scraper that collects articles from multiple sources and stores them in SQLite.

**Entry point**: `scraper.py` - orchestrates scraping, runs each source with 2-second delays, handles errors gracefully

**Database layer**: `db.py` - SQLite operations (init, insert with duplicate handling via UNIQUE on url, query, cleanup)

**Source scrapers** (`sources/`):
- `bbc.py` - HTML scraping via BeautifulSoup, looks for `/news/articles/` links
- `ap.py` - HTML scraping, uses `h3.PagePromo-title` selectors
- `google_news.py` - RSS feed parsing via lxml, uses topic feed URLs (encoded topic IDs)

Each source module exports a `scrape()` function that returns a list of article dicts with keys: `source`, `url`, `title`, `published_at`, `scraped_at`.

**Database**: `articles.db` - location controlled by `NEWS_SCRAPER_DB_PATH` env var (defaults to project root)

## Adding New Sources

1. Create `sources/newsource.py` with a `scrape()` function
2. Import and add to `sources` list in `scraper.py`
3. Update `get_article_count()` display in scraper summary

## Deployment

See `DEPLOYMENT.md` for DigitalOcean droplet deployment alongside polymarket-scanner.

## Notes

- Reuters is blocked (JS challenge) - that's why we use BBC instead
- Google News RSS returns redirect URLs, not direct article links
- Always use `python3` not `python`
- Set `NEWS_SCRAPER_DB_PATH` env var to customize database location (production uses `/var/lib/news-scraper/articles.db`)
