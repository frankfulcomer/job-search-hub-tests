from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pages.dom import fill_text, set_value_via_js

_JS_ASSIGNED_FIELDS = {"effective_at"}


class StatusChangePage:
    """The status-change form (``/applications/<id>/status``)."""

    def __init__(self, driver, base_url, application_id):
        self.driver = driver
        self.base_url = base_url
        self.application_id = application_id

    def load(self):
        self.driver.get(f"{self.base_url}/applications/{self.application_id}/status")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "status-change-form"))
        )
        return self

    def _field(self, field_id):
        return self.driver.find_element(By.ID, field_id)

    def set_status_name(self, status_name):
        Select(self._field("status_name")).select_by_value(status_name)
        return self

    def set_field(self, field_id, value):
        element = self._field(field_id)
        if field_id in _JS_ASSIGNED_FIELDS:
            set_value_via_js(self.driver, element, value or "")
        else:
            fill_text(element, value)
        return self

    def submit(self):
        self._field("submit-status-change").click()
        return self

    def wait_for_detail_redirect(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.url_to_be(f"{self.base_url}/applications/{self.application_id}")
        )
        return self

    @property
    def error_message(self):
        elements = self.driver.find_elements(By.ID, "form-error")
        return elements[0].text if elements else None
