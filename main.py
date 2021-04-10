# import os
# from selenium import webdriver
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from login import login
# from get_stories import get_stories
# from get_posts import get_posts
# from time import sleep
#
#
#
#
#
# path = "C:\Program Files (x86)\chromedriver.exe"
# driver = webdriver.Chrome(path)
# driver.maximize_window()
#
# url = 'https://www.instagram.com/'
# driver.get(url)
# login(driver, WebDriverWait, EC, By)
# usernames = ["gal_gadot", "cescf4bregas","liques","chelseafc"]
#
#
# def main():
#     for username in usernames:
#         sleep(1)
#         get_stories(url, username, driver, sleep, WebDriverWait, EC, By)
#         get_posts(driver, url, username, WebDriverWait, EC, By, sleep)
#
#
# while True:
#     main()
#     sleep(30)
