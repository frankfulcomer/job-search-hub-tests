from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class HomePage:
    """Job Hub's home page (``/``)."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def load(self):
        self.driver.get(self.base_url + "/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#home-page h2"))
        )
        return self

    @property
    def title(self):
        return self.driver.title

    @property
    def welcome_heading_text(self):
        return self.driver.find_element(By.CSS_SELECTOR, "#home-page h2").text
