"""Small helpers shared by the test modules.

``expected_stored_timestamp`` reproduces the persisted-timestamp format
documented in the application's ADR 0001 (ISO-8601 UTC, millisecond
precision, literal "Z" suffix) so SQL assertions can compute an expected
value independently, without importing the application's own formatting
function.
"""

from datetime import datetime

from pages.new_application_page import NewApplicationPage

DEFAULT_COMPANY_NAME = "Acme Testing Corp"
DEFAULT_JOB_TITLE = "QA Automation Engineer"
DEFAULT_SOURCE_NAME = "Company Website"
DEFAULT_APPLICATION_DATE = "2024-01-15"
DEFAULT_INITIAL_STATUS_EFFECTIVE_AT = "2024-01-15T09:00"


def expected_stored_timestamp(local_datetime_value):
    parsed = datetime.fromisoformat(local_datetime_value)
    return parsed.strftime("%Y-%m-%dT%H:%M:%S.") + f"{parsed.microsecond // 1000:03d}Z"


def create_application_via_ui(
    driver,
    app_server,
    *,
    company_name=DEFAULT_COMPANY_NAME,
    job_title=DEFAULT_JOB_TITLE,
    source_name=DEFAULT_SOURCE_NAME,
    application_date=DEFAULT_APPLICATION_DATE,
    initial_status_effective_at=DEFAULT_INITIAL_STATUS_EFFECTIVE_AT,
):
    """Create an application through the real UI form and wait for the list
    redirect that confirms it was saved.

    Returns the job title used, so the caller can look up the resulting
    application id afterward (e.g. via ApplicationListPage) without
    assuming any particular primary-key value.
    """
    page = NewApplicationPage(driver, app_server.base_url).load()
    page.set_field("company_name", company_name)
    page.set_field("job_title", job_title)
    page.set_field("application_date", application_date)
    page.set_field("source_name", source_name)
    page.set_field("initial_status_effective_at", initial_status_effective_at)
    page.submit()
    page.wait_for_list_redirect()
    return job_title
