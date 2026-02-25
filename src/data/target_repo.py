import csv
import logging
from dataclasses import dataclass, field
from src.config import TARGETS_CSV

logger = logging.getLogger(__name__)


@dataclass
class TargetAccount:
    username: str
    scrape_stories: bool
    scrape_posts: bool
    client_data: list = field(default_factory=list)


def load_targets() -> list[TargetAccount]:
    """
    Reads targets.csv and returns a list of TargetAccount dataclasses.

    Expected columns:
        username, is_story, is_post, [client_data_cols...]
    """
    targets = []
    try:
        with open(TARGETS_CSV, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if not row or not row[0].strip():
                    continue
                targets.append(TargetAccount(
                    username=row[0].strip(),
                    scrape_stories=row[1].strip().upper() == "TRUE" if len(row) > 1 else False,
                    scrape_posts=row[2].strip().upper() == "TRUE" if len(row) > 2 else False,
                    client_data=row[3:28] if len(row) > 3 else [],
                ))
    except FileNotFoundError:
        logger.error("Targets file not found: %s", TARGETS_CSV)
    return targets
