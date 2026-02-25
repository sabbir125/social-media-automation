import os
from os import path
from dotenv import load_dotenv

load_dotenv()

INSTAGRAM_URL = "https://www.instagram.com/"
CHROME_DRIVER_PATH = path.join(os.getcwd(), "storage", "chromedriver.exe")

MONGO_URI = os.getenv("MONGO_URI", "")
ACCOUNTS_CSV = os.getenv("ACCOUNTS_CSV", "data/accounts.csv")
TARGETS_CSV = os.getenv("TARGETS_CSV", "data/targets.csv")
SCHEDULE_INTERVAL_SEC = int(os.getenv("SCHEDULE_INTERVAL_SEC", "60"))
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

if not MONGO_URI:
    raise EnvironmentError("MONGO_URI is not set. Copy .env.example to .env and configure it.")
