import logging
from dataclasses import dataclass

from src.config import INSTAGRAM_URL
from src.core.auth import get_authenticated_driver
from src.core.scraper import get_stories, get_posts
from src.data.account_repo import Account, remove_account
from src.data.target_repo import TargetAccount, load_targets
from src.infrastructure.driver import quit_driver
from src.core.errors import check_network_error

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    username: str
    links: list
    client_data: list


def _rotate_account(current_account: Account, driver):
    """Removes the bad account, closes the driver, and authenticates a new one."""
    logger.warning("Rotating account away from: %s", current_account.username)
    remove_account(current_account)
    quit_driver(driver)
    return get_authenticated_driver(INSTAGRAM_URL)  # raises if no accounts left


def _scrape_target(target: TargetAccount, driver, account: Account):
    """
    Scrapes stories and/or posts for a single target.
    Returns (combined_links, driver, account) — driver/account may change on rotation.
    """
    combined = []

    if target.scrape_stories:
        result = get_stories(target.username, driver, INSTAGRAM_URL)
        if not result["success"] and result["error"] == "account":
            driver, account = _rotate_account(account, driver)
            result = get_stories(target.username, driver, INSTAGRAM_URL)
        if result["success"]:
            combined += result["data"]

    if target.scrape_posts:
        result = get_posts(target.username, driver, INSTAGRAM_URL)
        if not result["success"] and result["error"] == "account":
            driver, account = _rotate_account(account, driver)
            result = get_posts(target.username, driver, INSTAGRAM_URL)
        if result["success"]:
            combined += result["data"]

    return combined, driver, account


def run() -> bool:
    """
    Main scrape cycle. Iterates over all targets and scrapes stories/posts.
    Returns True on completion, False on unrecoverable error.
    """
    try:
        driver, account = get_authenticated_driver(INSTAGRAM_URL)
    except RuntimeError as e:
        logger.error("Cannot start scrape cycle: %s", e)
        return False

    targets = load_targets()
    if not targets:
        logger.error("No targets loaded. Check %s", "data/targets.csv")
        quit_driver(driver)
        return False

    results: list[ScrapeResult] = []

    for target in targets:
        logger.info("Processing: %s (stories=%s, posts=%s)",
                    target.username, target.scrape_stories, target.scrape_posts)
        try:
            links, driver, account = _scrape_target(target, driver, account)
            if links:
                results.append(ScrapeResult(target.username, links, target.client_data))
                logger.info("Collected %d items for %s", len(links), target.username)
        except RuntimeError as e:
            logger.error("Account pool exhausted during scrape: %s", e)
            return False
        except Exception:
            logger.exception("Unexpected error on target: %s", target.username)
            check_network_error(driver)
            quit_driver(driver)
            return False

    quit_driver(driver)
    logger.info("Cycle complete. Processed %d targets, collected data for %d.", len(targets), len(results))
    return True
