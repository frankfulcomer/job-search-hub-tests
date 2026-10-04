import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

_PATH = "/applications"
_VIEW_LINK_ID_RE = re.compile(r"^view-application-(\d+)$")


class ApplicationListPage:
    """The application list (``/applications``)."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def load(self):
        self.driver.get(self.base_url + _PATH)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "applications-list-page"))
        )
        return self

    def application_id_for_job_title(self, job_title, timeout=10):
        """Find the application id for the row whose job-title link has this
        exact text, without assuming any particular primary-key value."""

        def _find(driver):
            for link in driver.find_elements(By.CSS_SELECTOR, "a[id^='view-application-']"):
                if link.text == job_title:
                    match = _VIEW_LINK_ID_RE.match(link.get_attribute("id"))
                    if match:
                        return int(match.group(1))
            return False

        return WebDriverWait(self.driver, timeout).until(_find)

    def open_application(self, job_title):
        application_id = self.application_id_for_job_title(job_title)
        self.driver.find_element(By.ID, f"view-application-{application_id}").click()
        return application_id

    def row_cell_texts(self, application_id):
        cells = self.driver.find_elements(
            By.CSS_SELECTOR, f"#application-row-{application_id} td"
        )
        return [cell.text for cell in cells]
