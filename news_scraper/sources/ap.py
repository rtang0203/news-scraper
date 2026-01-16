import logging
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

BASE_URL = "https://apnews.com"
# AP News main page covers multiple topics
SECTIONS = ["", "/world-news", "/business", "/technology"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def scrape_section(section):
    """Scrape a single AP News section and return list of articles."""
    url = f"{BASE_URL}{section}"
    articles = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # AP News uses h3.PagePromo-title for headlines
        headlines = soup.find_all("h3", class_="PagePromo-title")

        seen_urls = set()
        for headline in headlines:
            link = headline.find("a", href=True)
            if not link:
                continue

            href = link.get("href", "")

            # Only process article links
            if "/article/" not in href:
                continue

            # Build full URL if relative
            if href.startswith("/"):
                full_url = f"{BASE_URL}{href}"
            elif not href.startswith("http"):
                full_url = f"{BASE_URL}/{href}"
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
                "source": "ap",
                "url": full_url,
                "title": title,
                "published_at": None,  # Timestamps not reliably in list views
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            })

        logger.info(f"AP {section or '/'}: found {len(articles)} articles")

    except requests.RequestException as e:
        logger.error(f"AP {section or '/'}: request failed - {e}")
    except Exception as e:
        logger.error(f"AP {section or '/'}: parsing failed - {e}")

    return articles


def scrape():
    """Scrape all AP News sections and return combined list of articles."""
    all_articles = []
    seen_urls = set()

    for section in SECTIONS:
        articles = scrape_section(section)

        for article in articles:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                all_articles.append(article)

    logger.info(f"AP total: {len(all_articles)} unique articles")
    return all_articles
