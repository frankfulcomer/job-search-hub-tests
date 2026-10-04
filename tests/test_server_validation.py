"""Server validation and recovery (FR-011): values the browser's own
constraint validation lets through, but that the application itself must
still reject, with a field-specific error, retained valid input, and no
partial writes. One case also demonstrates correcting the invalid value
and resubmitting successfully."""

from pages.application_list_page import ApplicationListPage
from pages.new_application_page import NewApplicationPage

VALID_JOB_TITLE = "Server Validation Role"
VALID_SOURCE_NAME = "Server Validation Source"
PAST_APPLICATION_DATE = "2023-05-10"
PAST_EFFECTIVE_AT = "2023-05-10T10:00"

_TABLES = ("application", "company", "source", "location", "application_status_history")


def _assert_nothing_written(app_db):
    for table in _TABLES:
        count = app_db.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"]
        assert count == 0, f"expected no rows in {table}, found {count}"


def test_whitespace_only_required_text_is_rejected_then_corrected(
    driver, app_server, app_db
):
    page = NewApplicationPage(driver, app_server.base_url).load()
    page.set_field("company_name", "   ")
    page.set_field("job_title", VALID_JOB_TITLE)
    page.set_field("application_date", PAST_APPLICATION_DATE)
    page.set_field("source_name", VALID_SOURCE_NAME)
    page.set_field("initial_status_effective_at", PAST_EFFECTIVE_AT)
    page.submit_expecting_error()

    assert page.current_url == app_server.base_url + "/applications/new"
    assert page.error_message == "company_name: is required"
    assert page.field_is_marked_invalid("company_name")
    # Valid input already entered is preserved, not lost, alongside the error.
    assert page.field_value("job_title") == VALID_JOB_TITLE
    assert page.field_value("source_name") == VALID_SOURCE_NAME
    assert page.field_value("application_date") == PAST_APPLICATION_DATE
    _assert_nothing_written(app_db)

    # Correct the one invalid field and resubmit; everything else was retained.
    page.set_field("company_name", "Whitespace Recovery Co")
    page.submit()
    page.wait_for_list_redirect()

    application_id = ApplicationListPage(
        driver, app_server.base_url
    ).application_id_for_job_title(VALID_JOB_TITLE)
    saved = app_db.execute(
        "SELECT c.name AS company_name FROM application a "
        "JOIN company c ON c.company_id = a.company_id "
        "WHERE a.application_id = ?",
        (application_id,),
    ).fetchone()
    assert saved["company_name"] == "Whitespace Recovery Co"


def test_missing_retrospective_initial_status_time_is_rejected(
    driver, app_server, app_db
):
    page = NewApplicationPage(driver, app_server.base_url).load()
    page.set_field("company_name", "Retrospective Co")
    page.set_field("job_title", VALID_JOB_TITLE)
    page.set_field("application_date", PAST_APPLICATION_DATE)
    page.set_field("source_name", VALID_SOURCE_NAME)
    # initial_status_effective_at left blank; initial_status_name left at
    # its default (APPLIED). A past application_date makes this a
    # retrospective entry, which requires an explicit effective time.
    page.submit_expecting_error()

    assert page.current_url == app_server.base_url + "/applications/new"
    assert page.error_message == (
        "initial_status_effective_at: is required unless the initial "
        "status is APPLIED and the application date is today"
    )
    assert page.field_is_marked_invalid("initial_status_effective_at")
    _assert_nothing_written(app_db)


def test_compensation_min_above_max_is_rejected(driver, app_server, app_db):
    page = NewApplicationPage(driver, app_server.base_url).load()
    page.set_field("company_name", "Compensation Co")
    page.set_field("job_title", VALID_JOB_TITLE)
    page.set_field("application_date", PAST_APPLICATION_DATE)
    page.set_field("source_name", VALID_SOURCE_NAME)
    page.set_field("initial_status_effective_at", PAST_EFFECTIVE_AT)
    page.set_field("compensation_min", "100000")
    page.set_field("compensation_max", "50000")
    page.set_field("compensation_basis", "ANNUAL")
    page.submit_expecting_error()

    assert page.current_url == app_server.base_url + "/applications/new"
    assert page.error_message == "compensation_min: must not exceed compensation_max"
    assert page.field_is_marked_invalid("compensation_min")
    _assert_nothing_written(app_db)
