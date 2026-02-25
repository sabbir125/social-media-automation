import os
from os import path

INSTAGRAM_URL = "https://www.instagram.com/"
CHROME_DRIVER_PATH = path.join(os.getcwd(), "storage", "chromedriver.exe")

DB_URI = "mongodb+srv://test:test@cluster0.nqwsp.mongodb.net/database?retryWrites=true&w=majority"

ACCOUNTS_CSV = "data/accounts.csv"
TARGETS_CSV = "data/targets.csv"

SCHEDULE_INTERVAL_SEC = 60
