from selenium import webdriver
from src.config import CHROME_DRIVER_PATH


def open_driver(url):
    try:
        driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        driver.maximize_window()
        driver.get(url)
        return {"success": True, "driver": driver}
    except Exception as e:
        print(f"Driver error: {e}")
        return {"success": False, "error": str(e)}


def close_driver(driver):
    driver.quit()
    print("Driver closed.")
    return {"success": True}
