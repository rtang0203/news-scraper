import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Google News RSS topic feeds (US English)
TOPICS = {
    "world": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB",
    "us": "https://news.google.com/rss/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNRGxqTjNjd0VnSmxiaWdBUAE",
    "business": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "technology": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "sports": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def parse_pub_date(pub_date_str):
    """Parse RSS pubDate to ISO format."""
    if not pub_date_str:
        return None
    try:
        dt = parsedate_to_datetime(pub_date_str)
        return dt.isoformat()
    except Exception:
        return None


def scrape_topic(topic_name, url):
    """Scrape a single Google News topic feed."""
    articles = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "xml")
        items = soup.find_all("item")

        for item in items:
            title_tag = item.find("title")
            link_tag = item.find("link")
            pub_date_tag = item.find("pubDate")
            source_tag = item.find("source")

            if not title_tag or not link_tag:
                continue

            title = title_tag.get_text(strip=True)
            url = link_tag.get_text(strip=True)

            # Extract original source name if available
            original_source = source_tag.get_text(strip=True) if source_tag else None

            # Append source to title for clarity (e.g., "Headline - Reuters")
            if original_source and not title.endswith(f"- {original_source}"):
                display_title = f"{title} - {original_source}"
            else:
                display_title = title

            articles.append({
                "source": "google_news",
                "url": url,
                "title": display_title,
                "published_at": parse_pub_date(pub_date_tag.get_text() if pub_date_tag else None),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "topic": topic_name,  # Extra metadata
            })

        logger.info(f"Google News {topic_name}: found {len(articles)} articles")

    except requests.RequestException as e:
        logger.error(f"Google News {topic_name}: request failed - {e}")
    except Exception as e:
        logger.error(f"Google News {topic_name}: parsing failed - {e}")

    return articles


def scrape():
    """Scrape all Google News topics and return combined list of articles."""
    all_articles = []
    seen_urls = set()

    for topic_name, url in TOPICS.items():
        articles = scrape_topic(topic_name, url)

        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                # Remove topic key before inserting (not in DB schema)
                article.pop("topic", None)
                all_articles.append(article)

    logger.info(f"Google News total: {len(all_articles)} unique articles")
    return all_articles
