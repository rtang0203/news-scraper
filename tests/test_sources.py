"""Tests for news source scrapers."""

import sys
from pathlib import Path

# Add news_scraper to path so we can import the sources
sys.path.insert(0, str(Path(__file__).parent.parent / "news_scraper"))

import pytest
from sources import bbc, ap, google_news


REQUIRED_KEYS = {"source", "url", "title", "published_at", "scraped_at"}


class TestBBC:
    def test_scrape_returns_articles(self):
        """BBC scraper should return a non-empty list of articles."""
        articles = bbc.scrape()
        assert len(articles) > 0, "BBC scraper returned no articles"

    def test_article_structure(self):
        """BBC articles should have all required keys."""
        articles = bbc.scrape()
        for article in articles[:5]:
            assert REQUIRED_KEYS.issubset(article.keys()), f"Missing keys in article: {article}"
            assert article["source"] == "bbc"
            assert article["url"].startswith("https://www.bbc.com")
            assert len(article["title"]) > 0


class TestAP:
    def test_scrape_returns_articles(self):
        """AP scraper should return a non-empty list of articles."""
        articles = ap.scrape()
        assert len(articles) > 0, "AP scraper returned no articles"

    def test_article_structure(self):
        """AP articles should have all required keys."""
        articles = ap.scrape()
        for article in articles[:5]:
            assert REQUIRED_KEYS.issubset(article.keys()), f"Missing keys in article: {article}"
            assert article["source"] == "ap"
            assert "apnews.com" in article["url"]
            assert len(article["title"]) > 0


class TestGoogleNews:
    def test_scrape_returns_articles(self):
        """Google News scraper should return a non-empty list of articles."""
        articles = google_news.scrape()
        assert len(articles) > 0, "Google News scraper returned no articles"

    def test_article_structure(self):
        """Google News articles should have all required keys."""
        articles = google_news.scrape()
        for article in articles[:5]:
            assert REQUIRED_KEYS.issubset(article.keys()), f"Missing keys in article: {article}"
            assert article["source"] == "google_news"
            assert "news.google.com" in article["url"]
            assert len(article["title"]) > 0

    def test_has_published_at(self):
        """Google News articles should have published_at timestamps."""
        articles = google_news.scrape()
        articles_with_timestamp = [a for a in articles if a["published_at"] is not None]
        assert len(articles_with_timestamp) > 0, "No Google News articles have timestamps"
