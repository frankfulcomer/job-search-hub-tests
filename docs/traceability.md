# Job Search Hub External Test Traceability

## Purpose

This document maps Job Search Hub Phase 1 functional requirements to external
test coverage maintained in this repository.

The matrix is intentionally lightweight. It identifies where Selenium provides
useful browser-level verification without requiring every requirement to have
external automated coverage.

## Functional Requirements

| Requirement | Area | External Test Approach | Status |
|---|---|---|---|
| FR-001 | Record an Application | `tests/test_create_application.py::test_create_and_read_application` (create via UI); `tests/test_server_validation.py` (whitespace-only required text, missing retrospective initial status time) | Partial |
| FR-002 | Detect Potential Duplicate Applications | Selenium candidate | Planned |
| FR-003 | View Applications | `tests/test_job_hub_smoke.py::test_home_page_loads`; `tests/test_create_application.py` (list row display); `tests/test_status_history.py` (current-status list column after a change) | Partial |
| FR-004 | Search and Filter Applications | Selenium candidate | Planned |
| FR-005 | View Application Details | `tests/test_create_application.py` (detail field display); `tests/test_status_history.py` (status history display and ordering) | Partial |
| FR-006 | Edit an Application | Selenium candidate | Planned |
| FR-007 | Update Application Status | `tests/test_status_history.py::test_adding_a_later_status_updates_current_status_and_preserves_history` | Partial |
| FR-008 | Correct Application Status History | TBD | Not evaluated |
| FR-009 | Archive and Restore an Application | Selenium candidate | Planned |
| FR-010 | Manage and Reuse Reference Data | TBD | Not evaluated |
| FR-011 | Validate Input and Handle Errors | `tests/test_required_field_validation.py` (native browser-blocked required-field omission, parameterized over company/title/source/date); `tests/test_server_validation.py` (whitespace-only required text, missing retrospective initial status time, compensation min > max, one resubmission demonstrated) | Partial |

## Notes

"Selenium candidate" does not mean that every behavior within the requirement
will receive browser automation.

"Partial" means this repository exercises one or a few representative
workflows or validation paths for that requirement through a real browser -
not that the requirement's full behavior is covered end to end. These are
large requirements; a handful of external scenarios should not be read as
implying exhaustive coverage. Detailed validation, persistence, boundary,
and business-rule coverage for the remaining behavior continues to belong
at lower test levels (the application repository's own unit/integration/
Flask tests), consistent with the overall Job Search Hub test strategy.

Where a "Partial" row's test approach notes SQL verification (via the
`app_db` fixture in `tests/conftest.py`), that specifically covers the
persistence-integrity aspect of the requirement - that the expected rows
and relationships actually exist in the database - rather than only that
the page rendered the expected text. `test_create_application.py` and
`test_status_history.py` both verify persistence this way.

This matrix will be refined as individual test scenarios are designed and
implemented.
