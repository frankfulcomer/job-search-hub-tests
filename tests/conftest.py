import pytest
from selenium import webdriver


@pytest.fixture
def driver():
    browser = webdriver.Chrome()

    try:
        yield browser
    finally:
        browser.quit()