def test_browser_starts(driver):
    driver.get("about:blank")

    assert driver.title == ""