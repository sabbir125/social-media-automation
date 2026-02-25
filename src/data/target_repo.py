import csv
from src.config import TARGETS_CSV


def read_targets():
    with open(TARGETS_CSV, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        return [line for line in reader if line]


def get_usernames():
    return [row[0] for row in read_targets()]


def get_scrape_flags():
    """Returns list of [story_flag, post_flag] per target row."""
    return [row[1:3] for row in read_targets()]


def get_client_data():
    """Returns client metadata columns (3-28) per target row."""
    return [row[3:28] for row in read_targets()]
