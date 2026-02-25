import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from src.data.models import Data, LastLink, save_scraped_data, save_last_link
from src.core.errors import handle_error

STORY_TYPE = 1
POST_TYPE = 2


def _push_stories_to_db(username, driver, story_list):
    """Iterates through story pages and saves each to DB."""
    try:
        while "stories" in driver.current_url:
            save_scraped_data(username, driver.current_url, STORY_TYPE)
            story_list.append({"link": driver.current_url, "type": STORY_TYPE})
            print(f"{driver.current_url} saved.")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@class="FhutL"]'))
            ).click()
        return {"success": True, "data": story_list}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_stories(username, driver, url):
    profile_url = url + username + "/"
    story_url = url + "stories/" + username + "/"
    driver.get(story_url)
    story_list = []
    time.sleep(3)

    current = driver.current_url
    if current == profile_url:
        print(f"{username}: no story available.")
        save_last_link(username, story_list)
        return {"success": True, "data": story_list}
    elif current == url:
        print(f"{username}: story not visible.")
        save_last_link(username, story_list)
        return {"success": True, "data": story_list}

    last_doc = LastLink.objects(username=username).first()

    if last_doc:
        driver.get(last_doc.lastStory_link)
        time.sleep(3)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"View Story")]'))
            ).click()
        except Exception:
            try:
                driver.refresh()
                time.sleep(1)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"View Story")]'))
                ).click()
            except Exception:
                driver.refresh()
                err_type = handle_error(driver)["error_type"]
                if err_type in ("login", "try again", "challenge"):
                    return {"success": False, "error": "account"}
                elif err_type in ("private", "restricted", "doesn't exist"):
                    return {"success": False, "error": "other"}
                return {"success": False, "error": "unknown"}

        if "stories" in driver.current_url and Data.objects(link=driver.current_url):
            print(f"{driver.current_url} already in DB.")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[@class="FhutL"]'))
            ).click()
            if driver.current_url != url:
                _push_stories_to_db(username, driver, story_list)
                last_doc.delete()
    else:
        try:
            count = 0
            while count < 15:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="Rkqev "]'))
                ).click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//span[@class="_2dbep "]//parent::div[@class="RR-M- h5uC0"]')
                    )
                ).click()
                result = _push_stories_to_db(username, driver, story_list)
                if result["success"]:
                    break
                count += 1
        except Exception:
            try:
                driver.get(story_url)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@class="Rkqev "]'))
                ).click()
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//span[@class="_2dbep "]//parent::div[@class="RR-M- h5uC0"]')
                    )
                ).click()
                time.sleep(1)
                _push_stories_to_db(username, driver, story_list)
            except Exception:
                err_type = handle_error(driver)["error_type"]
                if err_type in ("login", "try again", "challenge"):
                    return {"success": False, "error": "account"}
                elif err_type in ("private", "restricted", "doesn't exist"):
                    return {"success": False, "error": "other"}
                return {"success": False, "error": "unknown"}

    save_last_link(username, story_list)
    return {"success": True, "data": story_list}


def get_posts(username, driver, url):
    post_list = []
    profile_url = url + username + "/"
    if driver.current_url != profile_url:
        driver.get(profile_url)

    try:
        all_posts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '(//div[@class="eLAPa"]//parent::a)'))
        )
        posts = all_posts[:5]
        time.sleep(1)
    except Exception:
        try:
            driver.refresh()
            all_posts = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '(//div[@class="eLAPa"]//parent::a)'))
            )
            posts = all_posts[:5]
            time.sleep(1)
        except Exception:
            err_type = handle_error(driver)["error_type"]
            if err_type in ("login", "try again", "challenge"):
                return {"success": False, "error": "account"}
            elif err_type in ("private", "restricted", "doesn't exist"):
                return {"success": False, "error": "other"}
            return {"success": False, "error": "unknown"}

    for post in posts:
        link = post.get_attribute("href")
        if Data.objects(link=link):
            print(f"{link} already in DB.")
            break
        save_scraped_data(username, link, POST_TYPE)
        post_list.append({"link": link, "type": POST_TYPE})
        print(f"{link} saved.")

    return {"success": True, "data": post_list}
