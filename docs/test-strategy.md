# Job Search Hub External Test Automation Strategy

## Purpose

This repository provides independent, black-box testing of Job Search Hub through
its externally observable user interface.

It implements the external automation portion of the overall Job Search Hub
Phase 1 test strategy.

The primary goals are to:

- Verify critical user workflows through a real browser.
- Provide maintainable regression coverage where browser-level testing adds value.
- Demonstrate practical Selenium WebDriver and Pytest implementation.
- Complement, rather than duplicate, lower-level testing in the application repository.

## Scope

This repository owns:

- Selenium WebDriver browser automation.
- Pytest-based test execution.
- Browser fixtures and configuration.
- Page Objects and other reusable UI interaction components where useful.
- Controlled test data required by external tests.
- External smoke and regression coverage.
- Browser-level failure evidence and reporting where useful.

This repository shall treat Job Search Hub as a system under test and shall not
import or directly exercise application implementation code.

## Test Selection

Selenium tests shall focus on important workflows and behavior for which execution
through a real browser provides meaningful additional confidence.

Initial candidates include:

- Recording an application.
- Viewing recorded applications.
- Editing application details.
- Duplicate-application warning and override.
- Application status changes and lifecycle display.
- Search, filtering, and sorting.
- Archive and restore workflows.
- User-visible validation behavior.

Selenium shall not be used to reproduce every validation, boundary, persistence,
or business-rule test already covered more effectively at a lower test level.

## Test Design Principles

Tests should be:

- Independent where practical.
- Repeatable.
- Readable.
- Deterministic.
- Focused on observable user behavior.
- Traceable to significant requirements or risks where useful.

Reusable browser interaction shall be separated from test intent when doing so
improves readability and maintainability.

Abstraction shall be introduced when it provides demonstrated value rather than
solely to create framework complexity.

## Test Environment and Data

Automated tests shall execute against a dedicated Job Search Hub test instance
and test database.

Tests shall never read, modify, or delete the user's personal Job Search Hub data.

Test scenarios shall establish the data required for execution in a controlled
and repeatable manner.

Test data shall be clearly identifiable as test data.

## Isolation, Fixtures, and Verification

Pytest fixtures (`tests/conftest.py`), not a manually started server or a
shared database, shall own the lifecycle of both the application instance
under test and its database for each test:

- A fresh, isolated SQLite file is created for the test, and the
  application is started as a dedicated subprocess against it on a
  freshly selected loopback port. Ordinary application startup creates
  schema and seeds reference data; this repository never resets or
  prepares that database by other means.
- The application process, its database connection, and the shared
  browser session shall all be released on test success, test failure,
  and fixture setup error alike. A fixture shall only ever terminate the
  process it itself started.
- Readiness is established by bounded polling of the running instance,
  not a fixed delay; waits for in-page state shall use explicit
  conditions rather than arbitrary sleeps.

Browser-level assertions verify what a user would observe. Where a
scenario specifically claims a persistence outcome (e.g., that a status
change produced exactly one new history record with specific values),
tests additionally open the exact fixture-owned SQLite file, read-only,
and verify it directly with explicit columns and joins. This SQL step is
a verification oracle only - it shall never create test data, call
application code, or connect to a database other than the current test's
own managed instance.

Failure diagnosis shall distinguish three categories: environment/
infrastructure failures (e.g., the browser or application process failing
to start), product defects (the application behaving incorrectly once
both are running), and test defects (an incorrect assertion or fixture).
Fixture setup failures are reported distinctly from assertion failures
within a test to make this distinction visible from the pytest output
itself.

This milestone's execution remains local-first and deliberately scoped: a
small, representative set of workflows verified through a real browser
and a real running instance, not exhaustive requirement coverage. See
`docs/traceability.md` for what is and is not covered.

## Execution

Pytest shall provide test discovery, execution, fixtures, and result reporting.

Selenium WebDriver shall provide browser automation using a supported
Chromium-based browser.

The initial implementation shall favor reliable local execution before adding
CI-specific complexity.

## Continuous Integration

GitHub Actions shall eventually execute the external automated test suite against
a known Job Search Hub version in an isolated environment.

CI shall be introduced after reliable local execution has been established.
Reliable local execution (including rerun and order independence) has now
been demonstrated, but CI itself remains an outstanding Phase 1 item for
this repository, not something this milestone introduces or claims as
complete.

Useful failure artifacts such as screenshots, logs, or test reports may be
preserved when they improve diagnosis.

## Traceability

`docs/traceability.md` shall provide a lightweight mapping between significant
Job Search Hub requirements and the external test coverage implemented in this
repository.

Not every requirement requires Selenium coverage.

A requirement may intentionally be covered primarily by unit, integration,
Flask application, manual, or exploratory testing in accordance with the overall
Job Search Hub test strategy.
