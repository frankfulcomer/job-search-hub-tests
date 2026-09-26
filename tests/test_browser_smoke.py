from selenium import webdriver
import time


def test_browser_starts():
    driver = webdriver.Chrome()
    print(driver.capabilities.get("browserName"))
    print(driver.capabilities.get("browserVersion"))

    try:
        driver.get("about:blank")
        time.sleep(3)
        assert driver.title == ""
    finally:
        driver.quit()