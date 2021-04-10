import os
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from login import login
from get_stories import get_stories
from get_posts import get_posts
from time import sleep

chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument(('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'))
driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), options=chrome_options)


#
# path = "C:\Program Files (x86)\chromedriver.exe"
# driver = webdriver.Chrome(path)
driver.maximize_window()

url = 'https://www.instagram.com/'
driver.get(url)
login(driver, WebDriverWait, EC, By)
usernames = ["gal_gadot", "cescf4bregas","liques","chelseafc"]


def main():
    for username in usernames:
        sleep(1)
        get_stories(url, username, driver, sleep, WebDriverWait, EC, By)
        get_posts(driver, url, username, WebDriverWait, EC, By, sleep)


while True:
    main()
    sleep(30)
