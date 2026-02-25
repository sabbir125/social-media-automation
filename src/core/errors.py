import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(str, Enum):
    PRIVATE = "private"
    RESTRICTED = "restricted"
    NOT_FOUND = "not_found"
    LOGIN_FAILED = "login_failed"
    RATE_LIMITED = "rate_limited"
    CHALLENGE = "challenge"
    NETWORK = "network"
    UNKNOWN = "unknown"


# Maps XPath → (ErrorType, log message)
_PAGE_ERROR_CHECKS = [
    (
        '//h2[contains(text(),"This Account is Private")]',
        ErrorType.PRIVATE,
        "Account is private.",
    ),
    (
        '//div[contains(text(),"You must be 99 years old")]',
        ErrorType.RESTRICTED,
        "Age-restricted profile.",
    ),
    (
        "//h2[contains(text(),\"Sorry, this page isn\")]",
        ErrorType.NOT_FOUND,
        "Username does not exist.",
    ),
    (
        '//p[@data-testid="login-error-message"]',
        ErrorType.LOGIN_FAILED,
        "Login failed — account flagged. Rotating account.",
    ),
    (
        '//p[contains(text(),"Please wait a few minutes")]',
        ErrorType.RATE_LIMITED,
        "Rate limited. Rotating account.",
    ),
]


def classify_page_error(driver) -> ErrorType:
    """
    Inspects the current page DOM and URL to classify the error.
    Returns an ErrorType enum value.
    """
    for xpath, error_type, message in _PAGE_ERROR_CHECKS:
        try:
            driver.find_element_by_xpath(xpath)
            logger.warning(message)
            return error_type
        except Exception:
            pass

    if "challenge" in driver.current_url or "restriction" in driver.current_url:
        logger.warning("Account challenged or restricted. Rotating account.")
        return ErrorType.CHALLENGE

    logger.warning("Unknown page error at: %s", driver.current_url)
    return ErrorType.UNKNOWN


def is_account_error(error_type: ErrorType) -> bool:
    """Returns True if the error means the current account should be rotated."""
    return error_type in (ErrorType.LOGIN_FAILED, ErrorType.RATE_LIMITED, ErrorType.CHALLENGE)


def is_target_error(error_type: ErrorType) -> bool:
    """Returns True if the error is about the target profile (skip it)."""
    return error_type in (ErrorType.PRIVATE, ErrorType.RESTRICTED, ErrorType.NOT_FOUND)


def check_network_error(driver) -> bool:
    """Returns True if a network error indicator is found on the page."""
    try:
        driver.find_element_by_xpath('//span[contains(text(),"No internet")]')
        logger.error("No internet connection detected.")
        return True
    except Exception:
        logger.error("Unknown network error.")
        return False
