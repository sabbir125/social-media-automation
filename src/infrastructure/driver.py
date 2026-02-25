import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.config import CHROME_DRIVER_PATH, HEADLESS

logger = logging.getLogger(__name__)


def _build_options() -> Options:
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    if HEADLESS:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1920,1080")
    return options


def create_driver(url: str):
    """
    Initialises a Chrome WebDriver and navigates to the given URL.
    Returns the driver instance or raises on failure.
    """
    try:
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=_build_options())
        if not HEADLESS:
            driver.maximize_window()
        # Make automation less detectable
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.get(url)
        logger.info("Driver opened: %s", url)
        return driver
    except Exception as e:
        logger.exception("Failed to start ChromeDriver: %s", e)
        raise


def quit_driver(driver):
    try:
        driver.quit()
        logger.info("Driver closed.")
    except Exception:
        pass
