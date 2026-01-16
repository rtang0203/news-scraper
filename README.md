# News Scraper

Collects headlines, URLs, and timestamps from BBC, AP News, and Google News. Stores articles in SQLite for later analysis.

## Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the scraper:

```bash
cd news_scraper
python3 scraper.py
```

View recent articles:

```bash
python3 scraper.py --recent
python3 scraper.py --recent --limit 50
```

Clean up old articles:

```bash
# Delete articles older than 3 days (default)
python3 scraper.py --cleanup

# Delete articles older than 1 day
python3 scraper.py --cleanup --days 1

# Delete articles older than 7 days
python3 scraper.py --cleanup --days 7
```

## Automated Scraping (cron)

### Mac

Edit your crontab:

```bash
crontab -e
```

Add these lines to scrape every 10 minutes and clean up daily at midnight:

```
*/10 * * * * cd /path/to/news-scraper/news_scraper && /path/to/news-scraper/venv/bin/python3 scraper.py >> /path/to/news-scraper/scrape.log 2>&1
0 0 * * * cd /path/to/news-scraper/news_scraper && /path/to/news-scraper/venv/bin/python3 scraper.py --cleanup >> /path/to/news-scraper/scrape.log 2>&1
```

Replace `/path/to/news-scraper` with your actual path.

### DigitalOcean

1. Create a droplet (Ubuntu recommended)

2. Clone this repo and set up the venv:
   ```bash
   git clone <your-repo-url>
   cd news-scraper
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up cron:
   ```bash
   crontab -e
   ```
   Add:
   ```
   */10 * * * * cd /home/user/news-scraper/news_scraper && /home/user/news-scraper/venv/bin/python3 scraper.py >> /home/user/news-scraper/scrape.log 2>&1
   0 0 * * * cd /home/user/news-scraper/news_scraper && /home/user/news-scraper/venv/bin/python3 scraper.py --cleanup >> /home/user/news-scraper/scrape.log 2>&1
   ```

4. (Optional) Set up log rotation to prevent log file growth:
   ```bash
   sudo nano /etc/logrotate.d/news-scraper
   ```
   Add:
   ```
   /home/user/news-scraper/scrape.log {
       daily
       rotate 7
       compress
       missingok
       notifempty
   }
   ```

## Database

Articles are stored in `articles.db` (SQLite) in the project root.

Schema:
- `id` - Auto-incrementing primary key
- `source` - News source (bbc, ap, google_news)
- `url` - Article URL (unique constraint prevents duplicates)
- `title` - Headline text
- `published_at` - Publication timestamp (if available)
- `scraped_at` - When we collected the article

Query the database directly:

```bash
sqlite3 articles.db "SELECT * FROM articles ORDER BY scraped_at DESC LIMIT 10;"
```

## Sources

- **BBC News** - World, Business, Technology sections
- **AP News** - Homepage, World, Business, Technology sections
- **Google News** - World, US, Business, Technology, Sports topic feeds

## Notes

- The scraper includes a 2-second delay between sources to be respectful
- Duplicate URLs are automatically skipped (unique constraint on URL)
- If a source fails, the scraper continues with other sources
- Logs go to stdout by default, redirect to file with `>> scrape.log 2>&1`
