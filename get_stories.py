from database import *


def get_stories(url, username, driver, sleep, WebDriverWait, EC, By):
    try:
        user_profile = url + username + "/"
        story_url = url + 'stories/' + username + "/"
        driver.get(story_url)
        sleep(2)

        if driver.current_url == user_profile:
            print("story not available")
        elif driver.current_url == url:
            print("story is not able to see")
        else:
            driver.get(user_profile)
            count = 0
            while count < 20:
                # driver.get(user_profile)
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//canvas[@class="CfWVH"]//parent::div[@class="RR-M- h5uC0"]'))).click()
                sleep(1)
                if "stories" in driver.current_url:
                    while "stories" in driver.current_url:
                        type = 1
                        story_link=driver.current_url

                        if Data.objects(link=driver.current_url):
                            print(story_link,"already pushed in Database !")
                        else:
                            model(username, story_link, type)
                            print(story_link,"successfully pushed in Database.")
                        WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//button[@class="FhutL"]'))).click()

                    break
                else:
                    count = count + 1
    except Exception as e:
        if "challenge" in driver.current_url:
            print("Your account is wasted , change account and try again later ")
            driver.quit()
            exit()
        else:
            print(e)
