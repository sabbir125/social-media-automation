from database import *


def get_posts(driver, url, username, WebDriverWait, EC, By, sleep):
    try:
        if driver.current_url == url:
            driver.get(url + username + "/")

        all_posts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '(//div[@class="_9AhH0"]//parent::div//parent::a)')))
        posts = all_posts[:5]
        for post in posts:
            sleep(1)
            post_link = post.get_attribute("href")
            type = 2
            if Data.objects(link=url):
                print(post_link, "already pushed in Database !")
            else:
                model(username, post_link, type)
                print(post_link, "successfully pushed in Database.")
    except Exception as e:
        if driver.find_element_by_xpath('//h2[contains(text(),"This Account is Private")]'):
            print("This Account is Private")
        elif "challenge" in driver.current_url:
            print("Your account is wasted , change account and try again later ")
            driver.quit()
            exit()
        else:
            print(e)
