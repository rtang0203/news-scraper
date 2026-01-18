# Deployment Guide - DigitalOcean Droplet

This guide deploys news-scraper alongside the existing polymarket-scanner service.

## Target Structure

```
/opt/news-scraper/              # Code
├── news_scraper/
│   ├── scraper.py
│   ├── db.py
│   └── sources/
├── venv/
├── requirements.txt
└── ...

/var/lib/news-scraper/          # Data
├── articles.db
└── scraper.log
```

## Prerequisites

- Existing droplet with polymarket-scanner running
- User `app` exists (same as polymarket-scanner)
- Python 3.12.3 installed

## Deployment Steps

### 1. Create directories

```bash
sudo mkdir -p /opt/news-scraper
sudo mkdir -p /var/lib/news-scraper
sudo chown -R app:app /opt/news-scraper
sudo chown -R app:app /var/lib/news-scraper
```

### 2. Clone the repository

```bash
sudo -u app git clone <your-repo-url> /opt/news-scraper
```

Or copy files manually:

```bash
# From your local machine
scp -r news_scraper requirements.txt root@<droplet-ip>:/opt/news-scraper/
ssh root@<droplet-ip> "chown -R app:app /opt/news-scraper"
```

### 3. Set up Python virtual environment

```bash
sudo -u app bash -c "cd /opt/news-scraper && python3 -m venv venv"
sudo -u app /opt/news-scraper/venv/bin/pip install -r /opt/news-scraper/requirements.txt
```

### 4. Create environment file

```bash
sudo nano /var/lib/news-scraper/.env
```

Add:

```
NEWS_SCRAPER_DB_PATH=/var/lib/news-scraper/articles.db
```

Set permissions:

```bash
sudo chown app:app /var/lib/news-scraper/.env
sudo chmod 600 /var/lib/news-scraper/.env
```

### 5. Test the scraper

```bash
sudo -u app /opt/news-scraper/venv/bin/python3 /opt/news-scraper/news_scraper/scraper.py
```

Verify the database was created:

```bash
ls -la /var/lib/news-scraper/
```

### 6. Set up cron job

Edit the app user's crontab:

```bash
sudo -u app crontab -e
```

Add these lines:

```cron
# Run news scraper every 10 minutes
*/10 * * * * /opt/news-scraper/venv/bin/python3 /opt/news-scraper/news_scraper/scraper.py >> /var/lib/news-scraper/scraper.log 2>&1

# Cleanup old articles daily at midnight
0 0 * * * /opt/news-scraper/venv/bin/python3 /opt/news-scraper/news_scraper/scraper.py --cleanup >> /var/lib/news-scraper/scraper.log 2>&1
```

### 7. Set up log rotation

```bash
sudo nano /etc/logrotate.d/news-scraper
```

Add:

```
/var/lib/news-scraper/scraper.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 app app
}
```

## Verification

Check cron is running:

```bash
sudo -u app crontab -l
```

Check logs after 10 minutes:

```bash
tail -f /var/lib/news-scraper/scraper.log
```

Check database:

```bash
sqlite3 /var/lib/news-scraper/articles.db "SELECT COUNT(*) FROM articles;"
sqlite3 /var/lib/news-scraper/articles.db "SELECT source, COUNT(*) FROM articles GROUP BY source;"
```

## Future: Adding Correlation Service

When you add the correlation service to polymarket-scanner, chain it after news-scraper in cron:

```cron
*/10 * * * * /opt/news-scraper/venv/bin/python3 /opt/news-scraper/news_scraper/scraper.py >> /var/lib/news-scraper/scraper.log 2>&1 && /opt/polymarket-scanner/venv/bin/python3 /opt/polymarket-scanner/correlate.py >> /var/log/polymarket-scanner/correlate.log 2>&1
```

The correlation service can access both databases:
- News: `/var/lib/news-scraper/articles.db`
- Polymarket: (wherever polymarket-scanner stores its data)

## Troubleshooting

**Scraper not running?**
```bash
# Check cron logs
grep CRON /var/log/syslog | tail -20

# Run manually to see errors
sudo -u app /opt/news-scraper/venv/bin/python3 /opt/news-scraper/news_scraper/scraper.py
```

**Permission denied?**
```bash
sudo chown -R app:app /opt/news-scraper
sudo chown -R app:app /var/lib/news-scraper
```

**Python packages missing?**
```bash
sudo -u app /opt/news-scraper/venv/bin/pip install -r /opt/news-scraper/requirements.txt
```
