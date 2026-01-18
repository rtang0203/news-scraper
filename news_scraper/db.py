import os
import sqlite3
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from production location if it exists, otherwise check project root
_prod_env = Path("/var/lib/news-scraper/.env")
if _prod_env.exists():
    load_dotenv(_prod_env)
load_dotenv()  # Also check project root for local dev

logger = logging.getLogger(__name__)

# Database path: use NEWS_SCRAPER_DB_PATH env var, or default to project root
_default_db_path = Path(__file__).parent.parent / "articles.db"
DB_PATH = Path(os.environ.get("NEWS_SCRAPER_DB_PATH", _default_db_path))


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            published_at TEXT,
            scraped_at TEXT NOT NULL
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON articles(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scraped_at ON articles(scraped_at)")

    conn.commit()
    conn.close()
    logger.info(f"Database initialized at {DB_PATH}")


def insert_articles(articles):
    """
    Insert articles into the database.
    Duplicates (by URL) are ignored gracefully.

    Returns tuple of (inserted_count, skipped_count).
    """
    conn = get_connection()
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for article in articles:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO articles (source, url, title, published_at, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                article["source"],
                article["url"],
                article["title"],
                article.get("published_at"),
                article["scraped_at"]
            ))

            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1

        except Exception as e:
            logger.error(f"Error inserting article {article.get('url')}: {e}")
            skipped += 1

    conn.commit()
    conn.close()

    return inserted, skipped


def get_recent_articles(limit=20, source=None):
    """
    Get recent articles, optionally filtered by source.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if source:
        cursor.execute("""
            SELECT * FROM articles
            WHERE source = ?
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (source, limit))
    else:
        cursor.execute("""
            SELECT * FROM articles
            ORDER BY scraped_at DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_article_count(source=None):
    """Get total article count, optionally by source."""
    conn = get_connection()
    cursor = conn.cursor()

    if source:
        cursor.execute("SELECT COUNT(*) FROM articles WHERE source = ?", (source,))
    else:
        cursor.execute("SELECT COUNT(*) FROM articles")

    count = cursor.fetchone()[0]
    conn.close()

    return count


def cleanup_old_articles(days=3):
    """
    Delete articles older than specified days.
    Returns the number of deleted articles.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.isoformat()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM articles WHERE scraped_at < ?", (cutoff_str,))
    count = cursor.fetchone()[0]

    cursor.execute("DELETE FROM articles WHERE scraped_at < ?", (cutoff_str,))
    conn.commit()
    conn.close()

    logger.info(f"Cleanup: deleted {count} articles older than {days} days")
    return count
