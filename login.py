def login(driver, WebDriverWait, EC, By):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="username"]'))).send_keys("yamon72220")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="password"]'))).send_keys("password4466%")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[contains(text(),"Log In")]'))).click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Not Now")]'))).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(text(),"Not Now")]'))).click()

    except Exception as e:
        if "challenge" in driver.current_url:
            print("Your account is wasted , change account and try again later ")
            driver.quit()
            exit()
        else:
            print(e)
            exit()
            driver.quit()
