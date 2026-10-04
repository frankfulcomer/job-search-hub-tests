"""Status/history (FR-007, FR-005): adding a later-effective status change
updates the current status everywhere it is displayed, while the original
history entry remains intact and both entries persist in chronological
order."""

from pages.application_detail_page import ApplicationDetailPage
from pages.application_list_page import ApplicationListPage
from pages.status_change_page import StatusChangePage
from tests.support import (
    DEFAULT_INITIAL_STATUS_EFFECTIVE_AT,
    create_application_via_ui,
    expected_stored_timestamp,
)

SCREENING_EFFECTIVE_AT = "2024-01-20T11:30"
SCREENING_NOTES = "Recruiter screen scheduled"


def test_adding_a_later_status_updates_current_status_and_preserves_history(
    driver, app_server, app_db
):
    job_title = create_application_via_ui(driver, app_server)
    application_id = ApplicationListPage(
        driver, app_server.base_url
    ).application_id_for_job_title(job_title)

    status_page = StatusChangePage(driver, app_server.base_url, application_id).load()
    status_page.set_status_name("SCREENING")
    status_page.set_field("effective_at", SCREENING_EFFECTIVE_AT)
    status_page.set_field("notes", SCREENING_NOTES)
    status_page.submit()
    status_page.wait_for_detail_redirect()

    detail = ApplicationDetailPage(driver, app_server.base_url, application_id)
    detail.wait_until_loaded()
    assert detail.field("current_status") == "SCREENING"

    rows = detail.status_history_rows()
    assert len(rows) == 2
    applied_row, screening_row = rows
    assert applied_row["status_name"] == "APPLIED"
    assert applied_row["effective_at"] == expected_stored_timestamp(
        DEFAULT_INITIAL_STATUS_EFFECTIVE_AT
    )
    assert applied_row["notes"] == "—"
    assert applied_row["is_current"] is False

    assert screening_row["status_name"] == "SCREENING"
    assert screening_row["effective_at"] == expected_stored_timestamp(
        SCREENING_EFFECTIVE_AT
    )
    assert screening_row["notes"] == SCREENING_NOTES
    assert screening_row["is_current"] is True

    list_row = (
        ApplicationListPage(driver, app_server.base_url)
        .load()
        .row_cell_texts(application_id)
    )
    assert list_row[5] == "SCREENING"  # current-status column

    history = app_db.execute(
        """
        SELECT st.name AS status_name, ash.effective_at, ash.notes
        FROM application_status_history ash
        JOIN status st ON st.status_id = ash.status_id
        WHERE ash.application_id = ?
        ORDER BY ash.effective_at ASC
        """,
        (application_id,),
    ).fetchall()
    assert len(history) == 2
    assert history[0]["status_name"] == "APPLIED"
    assert history[0]["effective_at"] == expected_stored_timestamp(
        DEFAULT_INITIAL_STATUS_EFFECTIVE_AT
    )
    assert history[0]["notes"] is None
    assert history[1]["status_name"] == "SCREENING"
    assert history[1]["effective_at"] == expected_stored_timestamp(
        SCREENING_EFFECTIVE_AT
    )
    assert history[1]["notes"] == SCREENING_NOTES
