"""Confirms the WebDriver/Chrome stack itself works, independently of
Job Search Hub. Deliberately does not start or depend on the application,
so a failure here points at the browser environment rather than the
product (docs/test-strategy.md)."""


def test_browser_starts(driver):
    driver.get("about:blank")

    assert driver.title == ""
