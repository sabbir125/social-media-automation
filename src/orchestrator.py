from src.config import INSTAGRAM_URL
from src.core.auth import get_authenticated_driver
from src.core.scraper import get_stories, get_posts
from src.data.account_repo import delete_account
from src.data.target_repo import get_usernames, get_scrape_flags, get_client_data
from src.infrastructure.driver import close_driver
from src.core.errors import handle_network_error


def _make_entry(username, links, client_data):
    if links:
        return {"username": username, "links": links, "client_data": client_data}
    return None


def run():
    auth = get_authenticated_driver(INSTAGRAM_URL)
    if not auth["success"]:
        return {"success": False, "error": "listEmpty"}

    driver = auth["driver"]
    account = auth["data"]
    usernames = get_usernames()
    scrape_flags = get_scrape_flags()
    client_data_list = get_client_data()
    results = []

    for i, username in enumerate(usernames):
        scrape_story = scrape_flags[i][0] == "TRUE"
        scrape_post = scrape_flags[i][1] == "TRUE"
        client_data = client_data_list[i]

        try:
            combined = []

            if scrape_story:
                story_result = get_stories(username, driver, INSTAGRAM_URL)
                if not story_result["success"]:
                    if story_result["error"] == "account":
                        delete_account(account)
                        close_driver(driver)
                        auth = get_authenticated_driver(INSTAGRAM_URL)
                        if not auth["success"]:
                            return {"success": False, "error": "listEmpty"}
                        driver, account = auth["driver"], auth["data"]
                        story_result = get_stories(username, driver, INSTAGRAM_URL)
                if story_result["success"]:
                    combined += story_result["data"]

            if scrape_post:
                post_result = get_posts(username, driver, INSTAGRAM_URL)
                if not post_result["success"]:
                    if post_result["error"] == "account":
                        delete_account(account)
                        close_driver(driver)
                        auth = get_authenticated_driver(INSTAGRAM_URL)
                        if not auth["success"]:
                            return {"success": False, "error": "listEmpty"}
                        driver, account = auth["driver"], auth["data"]
                        post_result = get_posts(username, driver, INSTAGRAM_URL)
                if post_result["success"]:
                    combined += post_result["data"]

            entry = _make_entry(username, combined, client_data)
            if entry:
                results.append(entry)
                print(entry)

        except Exception:
            driver.refresh()
            handle_network_error(driver)
            return {"success": False, "error": "network"}

    close_driver(driver)
    print(results)
    return {"success": True}
