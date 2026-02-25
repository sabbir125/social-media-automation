import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.data.models import Cookies, save_cookies as db_save_cookies
from src.data.account_repo import get_random_account, delete_account
from src.infrastructure.driver import open_driver, close_driver
from src.core.errors import handle_error


def login(driver, username, password):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="username"]'))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))).send_keys(password)
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(),"Log In")]'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Not Now")]'))).click()
    wait.until(EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Not Now")]'))).click()
    return {"success": True}


def persist_cookies(driver, username):
    cookies = driver.get_cookies()
    db_save_cookies(username, cookies)
    print("Cookies saved.")
    return {"success": True}


def login_with_cookies(driver, username, url):
    try:
        cookie_doc = Cookies.objects.get(acc_username=username)
        driver.delete_all_cookies()
        for cookie in cookie_doc.cookies:
            driver.add_cookie(cookie)
        print("Cookies loaded.")
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Not Now")]'))
        ).click()
        time.sleep(5)
        return {"success": True}
    except Exception:
        print("Cookies expired.")
        return {"success": False, "error": "expire_cookies"}


def get_authenticated_driver(url):
    """
    Picks a random account, opens a driver, and authenticates.
    Falls back to password login if cookies are expired or missing.
    Removes bad accounts and retries until one works or list is empty.
    """
    while True:
        result = get_random_account()
        if not result["success"]:
            print("Account list empty.")
            return {"success": False, "error": "listEmpty"}

        account = result["data"]
        username, password = account[0], account[1]

        driver_result = open_driver(url)
        if not driver_result["success"]:
            return {"success": False, "error": driver_result["error"]}
        driver = driver_result["driver"]

        try:
            if Cookies.objects(acc_username=username):
                cookie_result = login_with_cookies(driver, username, url)
                if not cookie_result["success"]:
                    Cookies.objects(acc_username=username).delete()
                    print("Expired cookies removed.")
                    login(driver, username, password)
                    persist_cookies(driver, username)
            else:
                login(driver, username, password)
                persist_cookies(driver, username)

            return {"success": True, "data": account, "driver": driver}

        except Exception:
            err_type = handle_error(driver)["error_type"]
            if err_type in ("login", "try again", "challenge"):
                delete_account(account)
                close_driver(driver)
