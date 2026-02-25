# Instagram Scraper

Automated Instagram scraper that collects stories and posts from target accounts using Selenium. Credentials are managed via CSV, sessions are persisted with cookies, and scraped data is stored in MongoDB.

## Features

- Scrapes stories and/or posts per target username
- Cookie-based session reuse to avoid repeated logins
- Automatic account rotation when an account gets flagged
- MongoDB storage for scraped links, last-seen story, and cookies
- Configurable scraping flags per target (story, post, or both)

## Project Structure

```
instagram-scraper/
├── src/
│   ├── config.py           # Constants: URLs, DB URI, file paths
│   ├── orchestrator.py     # Main scraping loop per username
│   ├── core/
│   │   ├── auth.py         # Login, cookie persistence, account selection
│   │   ├── scraper.py      # get_stories, get_posts logic
│   │   └── errors.py       # Error classification from page state
│   ├── data/
│   │   ├── models.py       # MongoDB models (Data, LastLink, Cookies)
│   │   ├── account_repo.py # Read/write Instagram credentials CSV
│   │   └── target_repo.py  # Read target usernames and scrape config
│   └── infrastructure/
│       └── driver.py       # Selenium WebDriver setup and teardown
├── storage/
│   └── chromedriver.exe    # ChromeDriver binary
├── data/
│   ├── accounts.csv        # Instagram credentials (username, password) — gitignored
│   └── targets.csv         # Target usernames with scrape flags and metadata
├── main.py                 # Entry point
├── Procfile                # Heroku worker config
└── requirements.txt
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Place `chromedriver.exe` in the `storage/` folder matching your Chrome version.  
   Download from: https://chromedriver.chromium.org/downloads

3. Configure `data/accounts.csv` with your Instagram credentials:
   ```
   username,password
   ```

4. Configure `data/targets.csv` with target accounts:
   ```
   username,scrape_story,scrape_post,...client_data_columns
   ```
   - `scrape_story` / `scrape_post`: `TRUE` or `FALSE`

5. Update `src/config.py` with your MongoDB URI.

## Running

```bash
python main.py
```

The scraper runs in a loop with a 60-second interval between cycles. It stops automatically if the account list is empty or a network error occurs.

## Data Types

| Type | Meaning |
|------|---------|
| 1    | Story   |
| 2    | Post    |

## Notes

- Accounts that fail (login error, challenge, rate limit) are automatically removed from `insta_account.csv`.
- Cookies are stored in MongoDB and reused on subsequent runs to reduce login frequency.
- The `LastLink` collection tracks the last scraped story per username to avoid re-scraping.
