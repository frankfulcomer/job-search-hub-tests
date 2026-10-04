from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

_DETAIL_FIELDS = {
    "job_title": "detail-job-title",
    "application_date": "detail-application-date",
    "current_status": "detail-current-status",
    "source": "detail-source",
    "company": "detail-company",
    "work_arrangement": "detail-work-arrangement",
    "employment_type": "detail-employment-type",
    "notes": "detail-notes",
}


class ApplicationDetailPage:
    """The application detail view (``/applications/<id>``)."""

    def __init__(self, driver, base_url, application_id):
        self.driver = driver
        self.base_url = base_url
        self.application_id = application_id

    def load(self):
        self.driver.get(f"{self.base_url}/applications/{self.application_id}")
        return self.wait_until_loaded()

    def wait_until_loaded(self, timeout=10):
        """Wait for this detail page to be showing, without navigating to
        it - for use right after a click (e.g. the list page's row link)
        already triggered navigation."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, "application-detail-page"))
        )
        return self

    def field(self, name):
        return self.driver.find_element(By.ID, _DETAIL_FIELDS[name]).text

    def go_to_change_status(self):
        self.driver.find_element(By.ID, "change-status-link").click()
        return self

    def status_history_rows(self):
        """Each status-history row, in the document's (ascending) order."""
        rows = self.driver.find_elements(
            By.CSS_SELECTOR, "#status-history-table tbody tr"
        )
        results = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            results.append(
                {
                    "status_name": cells[0].text.replace("(current)", "").strip(),
                    "effective_at": cells[1].text,
                    "notes": cells[2].text,
                    "is_current": "current-status" in row.get_attribute("class"),
                }
            )
        return results
