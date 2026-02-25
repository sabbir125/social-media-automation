import csv
import random
from src.config import ACCOUNTS_CSV


def read_accounts():
    with open(ACCOUNTS_CSV, "r") as f:
        rows = [line for line in csv.reader(f) if line]
    return rows


def get_random_account():
    accounts = read_accounts()
    if not accounts:
        return {"success": False, "error": "empty_list"}
    return {"success": True, "data": random.choice(accounts)}


def delete_account(account):
    accounts = read_accounts()
    if account in accounts:
        accounts.remove(account)
    with open(ACCOUNTS_CSV, "w", newline="") as f:
        csv.writer(f).writerows(accounts)
    print(f"{account} removed from accounts.")
    return {"success": True}
