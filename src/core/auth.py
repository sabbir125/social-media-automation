import logging
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from src.data.models import SessionCookies, save_session_cookies
from src.data.account_repo import Account, get_random_account, remove_account
from src.infrastructure.driver import create_driver, quit_driver
from src.core.errors import classify_page_error, is_account_error
from src.config import INSTAGRAM_URL

logger = logging.getLogger(__name__)

_WAIT_TIMEOUT = 10
_MAX_RETRIES = 5


def _wait(driver) -> WebDriverWait:
    return WebDriverWait(driver, _WAIT_TIMEOUT)


def _click_not_now(driver):
    """Dismisses Instagram's 'Save Login Info' and notification prompts."""
    for _ in range(2):
        try:
            _wait(driver).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"Not Now")]'))
            ).click()
        except TimeoutException:
            break


def login_with_password(driver, account: Account):
    """Performs a full username/password login."""
    logger.info("Logging in as: %s", account.username)
    _wait(driver).until(
        EC.presence_of_element_located((By.XPATH, '//input[@name="username"]'))
    ).send_keys(account.username)
    _wait(driver).until(
        EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))
    ).send_keys(account.password)
    _wait(driver).until(
        EC.element_to_be_clickable((By.XPATH, '//div[contains(text(),"Log In")]'))
    ).click()
    _click_not_now(driver)


def persist_cookies(driver, username: str):
    """Saves current browser cookies to DB for future sessions."""
    save_session_cookies(username, driver.get_cookies())
    logger.info("Session cookies saved for: %s", username)


def login_with_cookies(driver, username: str, url: str) -> bool:
    """
    Attempts to restore a session using stored cookies.
    Returns True on success, False if cookies are expired or missing.
    """
    cookie_doc = SessionCookies.objects(acc_username=username).first()
    if not cookie_doc:
        return False

    try:
        driver.delete_all_cookies()
        for cookie in cookie_doc.cookies:
            driver.add_cookie(cookie)
        driver.get(url)
        time.sleep(3)
        _click_not_now(driver)
        logger.info("Session restored via cookies for: %s", username)
        return True
    except Exception:
        logger.warning("Cookies expired for: %s", username)
        return False


def get_authenticated_driver(url: str = INSTAGRAM_URL):
    """
    Selects a random account and returns an authenticated WebDriver.

    Strategy:
      1. Try cookie-based login first (faster, less detectable).
      2. Fall back to password login and persist new cookies.
      3. On account errors, remove the account and retry with the next one.
      4. Raises RuntimeError if no valid accounts remain.
    """
    for attempt in range(_MAX_RETRIES):
        account = get_random_account()
        if account is None:
            raise RuntimeError("No accounts available. Add credentials to data/accounts.csv.")

        try:
            driver = create_driver(url)
        except Exception as e:
            raise RuntimeError(f"Could not start ChromeDriver: {e}") from e

        try:
            restored = login_with_cookies(driver, account.username, url)
            if not restored:
                SessionCookies.objects(acc_username=account.username).delete()
                login_with_password(driver, account)
                persist_cookies(driver, account.username)

            logger.info("Authenticated as: %s (attempt %d)", account.username, attempt + 1)
            return driver, account

        except Exception:
            error_type = classify_page_error(driver)
            if is_account_error(error_type):
                logger.warning("Removing bad account: %s (%s)", account.username, error_type)
                remove_account(account)
                quit_driver(driver)
            else:
                quit_driver(driver)
                raise

    raise RuntimeError(f"Failed to authenticate after {_MAX_RETRIES} attempts.")
