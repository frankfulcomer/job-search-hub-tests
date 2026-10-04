"""Required-field rejection (FR-011): clearing a required create-application
field is blocked by the browser's own constraint validation before the form
is ever submitted to the server. This is distinct from server validation
(see test_server_validation.py), which covers values the browser *does*
let through."""

import pytest

from pages.new_application_page import NewApplicationPage

COMPANY_NAME = "Required Field Co"
JOB_TITLE = "Required Field Role"
SOURCE_NAME = "Required Field Source"
APPLICATION_DATE = "2024-02-01"

_VALID_VALUES = {
    "company_name": COMPANY_NAME,
    "job_title": JOB_TITLE,
    "source_name": SOURCE_NAME,
    "application_date": APPLICATION_DATE,
}

_TABLES = ("application", "company", "source", "location", "application_status_history")


@pytest.mark.parametrize("omitted_field", sorted(_VALID_VALUES))
def test_omitting_a_required_field_is_blocked_natively(
    driver, app_server, app_db, omitted_field
):
    page = NewApplicationPage(driver, app_server.base_url).load()

    for field, value in _VALID_VALUES.items():
        if field == omitted_field:
            # The application-date field is pre-filled with today's date by
            # the server, so omitting it means explicitly clearing that
            # default rather than simply not typing anything.
            if field == "application_date":
                page.set_field(field, "")
            continue
        page.set_field(field, value)

    page.submit()

    assert page.field_is_natively_invalid(omitted_field)
    assert page.current_url == app_server.base_url + "/applications/new"

    for table in _TABLES:
        count = app_db.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        assert count == 0, f"expected no rows in {table}, found {count}"
