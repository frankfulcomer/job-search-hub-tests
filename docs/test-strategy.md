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