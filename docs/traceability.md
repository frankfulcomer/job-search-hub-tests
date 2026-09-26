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
| FR-001 | Record an Application | Selenium candidate | Planned |
| FR-002 | Detect Potential Duplicate Applications | Selenium candidate | Planned |
| FR-003 | View Applications | Selenium candidate | Planned |
| FR-004 | Search and Filter Applications | Selenium candidate | Planned |
| FR-005 | View Application Details | Selenium candidate | Planned |
| FR-006 | Edit an Application | Selenium candidate | Planned |
| FR-007 | Update Application Status | Selenium candidate | Planned |
| FR-008 | Correct Application Status History | TBD | Not evaluated |
| FR-009 | Archive and Restore an Application | Selenium candidate | Planned |
| FR-010 | Manage and Reuse Reference Data | TBD | Not evaluated |
| FR-011 | Validate Input and Handle Errors | Mixed coverage | Planned |

## Notes

"Selenium candidate" does not mean that every behavior within the requirement
will receive browser automation.

Detailed validation, persistence, boundary, and business-rule coverage should
remain at lower test levels when those levels provide faster and more reliable
verification.

This matrix will be refined as individual test scenarios are designed and
implemented.