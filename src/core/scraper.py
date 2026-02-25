import logging
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from src.data.models import ScrapedData, LastLink, save_scraped_link, upsert_last_link
from src.core.errors import classify_page_error, is_account_error, is_target_error, ErrorType

logger = logging.getLogger(__name__)

_WAIT_TIMEOUT = 10
_MAX_POSTS = 5
_MAX_STORY_PAGES = 15


def _wait(driver) -> WebDriverWait:
    return WebDriverWait(driver, _WAIT_TIMEOUT)


def _classify_and_raise(driver, context: str) -> ErrorType:
    """Classifies the current page error and returns the ErrorType."""
    error_type = classify_page_error(driver)
    logger.warning("[%s] Page error: %s", context, error_type)
    return error_type


def _navigate_with_retry(driver, url: str, context: str):
    """Navigates to a URL, retrying once on failure."""
    driver.get(url)
    time.sleep(2)
    if driver.current_url == url:
        return
    driver.refresh()
    time.sleep(2)


def _collect_story_pages(username: str, driver, story_list: list) -> bool:
    """
    Iterates through story pages clicking 'next', saving each URL.
    Returns True when all pages are consumed.
    """
    next_btn_xpath = '//button[@class="FhutL"]'
    while "stories" in driver.current_url:
        link = driver.current_url
        if save_scraped_link(username, link, ScrapedData.STORY):
            story_list.append({"link": link, "type": ScrapedData.STORY})
        try:
            _wait(driver).until(EC.presence_of_element_located((By.XPATH, next_btn_xpath))).click()
        except TimeoutException:
            break
    return True


def get_stories(username: str, driver, url: str) -> dict:
    """
    Scrapes all available stories for a username.

    Resumes from the last saved story link if one exists in DB.
    Returns {"success": True, "data": [...]} or {"success": False, "error": "account"|"target"|"unknown"}.
    """
    profile_url = f"{url}{username}/"
    story_url = f"{url}stories/{username}/"
    story_list = []

    _navigate_with_retry(driver, story_url, username)

    current = driver.current_url
    if current in (profile_url, url):
        logger.info("[%s] No stories available.", username)
        return {"success": True, "data": story_list}

    last_doc = LastLink.objects(username=username).first()

    if last_doc:
        _navigate_with_retry(driver, last_doc.last_story_link, username)
        try:
            _wait(driver).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"View Story")]'))
            ).click()
        except TimeoutException:
            error_type = _classify_and_raise(driver, username)
            if is_account_error(error_type):
                return {"success": False, "error": "account"}
            if is_target_error(error_type):
                return {"success": False, "error": "target"}
            return {"success": False, "error": "unknown"}

        # Skip already-saved story, then continue from next
        if "stories" in driver.current_url and ScrapedData.objects(link=driver.current_url).first():
            logger.debug("[%s] Resuming past already-saved story.", username)
            try:
                _wait(driver).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@class="FhutL"]'))
                ).click()
            except TimeoutException:
                pass

        if driver.current_url != url:
            _collect_story_pages(username, driver, story_list)
            last_doc.delete()
    else:
        # Fresh scrape — navigate into the story viewer
        try:
            for _ in range(_MAX_STORY_PAGES):
                _wait(driver).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="Rkqev "]'))
                ).click()
                _wait(driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//span[@class="_2dbep "]//parent::div[@class="RR-M- h5uC0"]')
                    )
                ).click()
                if _collect_story_pages(username, driver, story_list):
                    break
        except TimeoutException:
            try:
                _navigate_with_retry(driver, story_url, username)
                _wait(driver).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="Rkqev "]'))
                ).click()
                _wait(driver).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//span[@class="_2dbep "]//parent::div[@class="RR-M- h5uC0"]')
                    )
                ).click()
                _collect_story_pages(username, driver, story_list)
            except TimeoutException:
                error_type = _classify_and_raise(driver, username)
                if is_account_error(error_type):
                    return {"success": False, "error": "account"}
                if is_target_error(error_type):
                    return {"success": False, "error": "target"}
                return {"success": False, "error": "unknown"}

    if story_list:
        upsert_last_link(username, story_list[-1]["link"])

    logger.info("[%s] Scraped %d stories.", username, len(story_list))
    return {"success": True, "data": story_list}


def get_posts(username: str, driver, url: str) -> dict:
    """
    Scrapes the latest posts (up to _MAX_POSTS) for a username.

    Stops early if a post is already in the DB (deduplication).
    Returns {"success": True, "data": [...]} or {"success": False, "error": "account"|"target"|"unknown"}.
    """
    post_list = []
    profile_url = f"{url}{username}/"

    if driver.current_url != profile_url:
        _navigate_with_retry(driver, profile_url, username)

    posts_xpath = '(//div[@class="eLAPa"]//parent::a)'

    try:
        all_posts = _wait(driver).until(
            EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
        )
    except TimeoutException:
        try:
            driver.refresh()
            time.sleep(2)
            all_posts = _wait(driver).until(
                EC.presence_of_all_elements_located((By.XPATH, posts_xpath))
            )
        except TimeoutException:
            error_type = _classify_and_raise(driver, username)
            if is_account_error(error_type):
                return {"success": False, "error": "account"}
            if is_target_error(error_type):
                return {"success": False, "error": "target"}
            return {"success": False, "error": "unknown"}

    for post in all_posts[:_MAX_POSTS]:
        link = post.get_attribute("href")
        saved = save_scraped_link(username, link, ScrapedData.POST)
        if not saved:
            # Hit an already-seen post — no need to go further back
            break
        post_list.append({"link": link, "type": ScrapedData.POST})

    logger.info("[%s] Scraped %d posts.", username, len(post_list))
    return {"success": True, "data": post_list}
