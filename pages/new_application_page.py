from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from pages.dom import fill_text, is_natively_invalid, set_value_via_js

_PATH = "/applications/new"

# Fields assigned through JavaScript (date/datetime-local) rather than
# send_keys; see pages/dom.py for why.
_JS_ASSIGNED_FIELDS = {"application_date", "initial_status_effective_at"}

# <select> fields: chosen with the Select helper rather than clear()/
# send_keys(), which only apply to editable text controls.
_SELECT_FIELDS = {"initial_status_name", "work_arrangement", "employment_type", "compensation_basis"}


class NewApplicationPage:
    """The "New Application" create form (``/applications/new``)."""

    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url

    def load(self):
        self.driver.get(self.base_url + _PATH)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "create-application-form"))
        )
        return self

    def _field(self, field_id):
        return self.driver.find_element(By.ID, field_id)

    def set_field(self, field_id, value):
        """Set any form field by its element id, using the right method for its type."""
        element = self._field(field_id)
        if field_id in _JS_ASSIGNED_FIELDS:
            set_value_via_js(self.driver, element, value or "")
        elif field_id in _SELECT_FIELDS:
            Select(element).select_by_value(value)
        else:
            fill_text(element, value)
        return self

    def field_value(self, field_id):
        return self._field(field_id).get_attribute("value")

    def field_is_natively_invalid(self, field_id):
        return is_natively_invalid(self.driver, self._field(field_id))

    def submit(self):
        self._field("submit-application").click()
        return self

    def wait_for_list_redirect(self, timeout=10):
        WebDriverWait(self.driver, timeout).until(
            EC.url_to_be(self.base_url + "/applications")
        )
        return self

    @property
    def error_message(self):
        elements = self.driver.find_elements(By.ID, "form-error")
        return elements[0].text if elements else None

    def field_is_marked_invalid(self, field_id):
        return self._field(field_id).get_attribute("aria-invalid") == "true"

    @property
    def current_url(self):
        return self.driver.current_url
