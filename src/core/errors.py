def handle_error(driver):
    """
    Inspects the current page to classify the error type.
    Returns one of: private, restricted, doesn't exist, login, try again, challenge, unknown
    """
    checks = [
        ('//h2[contains(text(),"This Account is Private")]', "private", "This Account is Private"),
        ('//div[contains(text(),"You must be 99 years old")]', "restricted", "Restricted profile"),
        ("//h2[contains(text(),\"Sorry, this page isn\")]", "doesn't exist", "Username doesn't exist"),
        ('//p[@data-testid="login-error-message"]', "login", "Account flagged, switching account"),
        ('//p[contains(text(),"Please wait a few minutes")]', "try again", "Rate limited, try again later"),
    ]

    for xpath, error_type, message in checks:
        try:
            driver.find_element_by_xpath(xpath)
            print(message)
            return {"error_type": error_type}
        except Exception:
            pass

    if "challenge" in driver.current_url or "restriction" in driver.current_url:
        print("Account challenged/restricted, switching account")
        return {"error_type": "challenge"}

    return {"error_type": "unknown"}


def handle_network_error(driver):
    try:
        driver.find_element_by_xpath('//span[contains(text(),"No internet")]')
        print("No internet connection")
    except Exception:
        print("Unknown network error, try again later")
    return {"success": True}
