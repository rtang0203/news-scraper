import logging
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://www.bbc.com"
SECTIONS = ["/news/world", "/news/business", "/news/technology"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def scrape_section(section):
    """Scrape a single BBC section and return list of articles."""
    url = f"{BASE_URL}{section}"
    articles = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Find all article links
        links = soup.find_all("a", href=True)

        seen_urls = set()
        for link in links:
            href = link.get("href", "")

            # Only process article links
            if "/news/articles/" not in href:
                continue

            # Build full URL
            if href.startswith("/"):
                full_url = f"{BASE_URL}{href}"
            else:
                full_url = href

            # Skip duplicates
            if full_url in seen_urls:
                continue

            # Get title text
            title = link.get_text(strip=True)

            # Skip links without meaningful titles
            if not title or len(title) < 10:
                continue

            seen_urls.add(full_url)

            articles.append({
                "source": "bbc",
                "url": full_url,
                "title": title,
                "published_at": None,  # BBC doesn't show timestamps in list view
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info(f"BBC {section}: found {len(articles)} articles")

    except requests.RequestException as e:
        logger.error(f"BBC {section}: request failed - {e}")
    except Exception as e:
        logger.error(f"BBC {section}: parsing failed - {e}")

    return articles


def scrape():
    """Scrape all BBC sections and return combined list of articles."""
    all_articles = []
    seen_urls = set()

    for section in SECTIONS:
        articles = scrape_section(section)

        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                all_articles.append(article)

    logger.info(f"BBC total: {len(all_articles)} unique articles")
    return all_articles
