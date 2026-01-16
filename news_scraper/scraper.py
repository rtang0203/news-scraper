#!/usr/bin/env python3
"""
News Scraper - Collects headlines from BBC and AP News.

Usage:
    python scraper.py           # Run scraper
    python scraper.py --recent  # Show recent articles
"""

import argparse
import logging
import sys
import time

from db import init_db, insert_articles, get_recent_articles, get_article_count
from sources import bbc, ap

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_scraper():
    """Run all scrapers and store results."""
    logger.info("Starting news scraper")

    # Initialize database
    init_db()

    all_articles = []
    sources = [
        ("BBC", bbc.scrape),
        ("AP", ap.scrape),
    ]

    for name, scrape_fn in sources:
        try:
            logger.info(f"Scraping {name}...")
            articles = scrape_fn()
            all_articles.extend(articles)
            logger.info(f"{name}: collected {len(articles)} articles")
        except Exception as e:
            logger.error(f"{name}: scraper failed - {e}")

        # Delay between sources to be respectful
        time.sleep(2)

    # Insert all articles
    if all_articles:
        inserted, skipped = insert_articles(all_articles)
        logger.info(f"Database: inserted {inserted}, skipped {skipped} duplicates")
    else:
        logger.warning("No articles collected")

    # Print summary
    print("\n" + "=" * 50)
    print("SCRAPE SUMMARY")
    print("=" * 50)
    print(f"Total collected: {len(all_articles)}")

    if all_articles:
        print(f"New articles:    {inserted}")
        print(f"Duplicates:      {skipped}")

    print(f"\nDatabase totals:")
    print(f"  BBC:   {get_article_count('bbc')} articles")
    print(f"  AP:    {get_article_count('ap')} articles")
    print(f"  Total: {get_article_count()} articles")
    print("=" * 50)


def show_recent(limit=20):
    """Display recent articles from the database."""
    articles = get_recent_articles(limit=limit)

    if not articles:
        print("No articles in database. Run the scraper first.")
        return

    print(f"\nMost Recent {len(articles)} Articles:")
    print("-" * 80)

    for article in articles:
        print(f"[{article['source'].upper()}] {article['title'][:70]}")
        print(f"         {article['url']}")
        print(f"         Scraped: {article['scraped_at']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="News Scraper - BBC and AP News")
    parser.add_argument(
        "--recent",
        action="store_true",
        help="Show recent articles instead of scraping",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of recent articles to show (default: 20)",
    )

    args = parser.parse_args()

    if args.recent:
        init_db()
        show_recent(limit=args.limit)
    else:
        run_scraper()


if __name__ == "__main__":
    main()
