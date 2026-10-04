"""Create and read an application: FR-001 (record), FR-003 (list display),
FR-005 (detail display), plus the persistence-integrity aspect of FR-011
verified by SQL rather than visible UI state alone."""

from pages.application_detail_page import ApplicationDetailPage
from pages.application_list_page import ApplicationListPage
from tests.support import (
    DEFAULT_APPLICATION_DATE,
    DEFAULT_COMPANY_NAME,
    DEFAULT_INITIAL_STATUS_EFFECTIVE_AT,
    DEFAULT_JOB_TITLE,
    DEFAULT_SOURCE_NAME,
    create_application_via_ui,
    expected_stored_timestamp,
)


def test_create_and_read_application(driver, app_server, app_db):
    job_title = create_application_via_ui(driver, app_server)

    list_page = ApplicationListPage(driver, app_server.base_url)
    application_id = list_page.application_id_for_job_title(job_title)
    row = list_page.row_cell_texts(application_id)
    assert row == [
        DEFAULT_COMPANY_NAME,
        DEFAULT_JOB_TITLE,
        "—",  # job location: not provided
        "—",  # work arrangement: not provided
        DEFAULT_APPLICATION_DATE,
        "APPLIED",
        DEFAULT_SOURCE_NAME,
    ]

    list_page.open_application(job_title)
    detail = ApplicationDetailPage(driver, app_server.base_url, application_id)
    detail.wait_until_loaded()
    assert detail.field("job_title") == DEFAULT_JOB_TITLE
    assert detail.field("application_date") == DEFAULT_APPLICATION_DATE
    assert detail.field("current_status") == "APPLIED"
    assert detail.field("source") == DEFAULT_SOURCE_NAME
    assert detail.field("company") == DEFAULT_COMPANY_NAME

    applications = app_db.execute(
        """
        SELECT a.application_id, a.job_title, a.application_date,
               c.name AS company_name, s.name AS source_name
        FROM application a
        JOIN company c ON c.company_id = a.company_id
        JOIN source s ON s.source_id = a.source_id
        """
    ).fetchall()
    assert len(applications) == 1
    application_row = applications[0]
    assert application_row["application_id"] == application_id
    assert application_row["job_title"] == DEFAULT_JOB_TITLE
    assert application_row["application_date"] == DEFAULT_APPLICATION_DATE
    assert application_row["company_name"] == DEFAULT_COMPANY_NAME
    assert application_row["source_name"] == DEFAULT_SOURCE_NAME

    history = app_db.execute(
        """
        SELECT ash.effective_at, st.name AS status_name
        FROM application_status_history ash
        JOIN status st ON st.status_id = ash.status_id
        WHERE ash.application_id = ?
        """,
        (application_id,),
    ).fetchall()
    assert len(history) == 1
    assert history[0]["status_name"] == "APPLIED"
    assert history[0]["effective_at"] == expected_stored_timestamp(
        DEFAULT_INITIAL_STATUS_EFFECTIVE_AT
    )
