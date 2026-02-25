import csv
import logging
import random
from dataclasses import dataclass
from src.config import ACCOUNTS_CSV

logger = logging.getLogger(__name__)


@dataclass
class Account:
    username: str
    password: str

    def as_row(self):
        return [self.username, self.password]


def _read_accounts() -> list[Account]:
    try:
        with open(ACCOUNTS_CSV, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            return [Account(row[0], row[1]) for row in reader if len(row) >= 2]
    except FileNotFoundError:
        logger.error("Accounts file not found: %s", ACCOUNTS_CSV)
        return []


def get_random_account() -> Account | None:
    accounts = _read_accounts()
    if not accounts:
        logger.warning("No accounts available in %s", ACCOUNTS_CSV)
        return None
    return random.choice(accounts)


def remove_account(account: Account):
    """Removes a flagged account from the CSV."""
    accounts = _read_accounts()
    accounts = [a for a in accounts if a.username != account.username]
    with open(ACCOUNTS_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["username", "password"])
        writer.writerows([a.as_row() for a in accounts])
    logger.warning("Removed account: %s", account.username)
