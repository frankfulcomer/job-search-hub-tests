# Job Search Hub Test Journal

## 2026-09-26 - External Test Repository Initialization

### Work Completed

- Created the `job-search-hub-tests` repository.
- Created an isolated Python virtual environment.
- Installed Selenium and Pytest.
- Established the initial repository structure:
  - `tests/`
  - `pages/`
  - `docs/`
  - `conftest.py`
  - `requirements.txt`
- Created the external test automation strategy.
- Created the initial functional-requirement traceability matrix.
- Verified Selenium WebDriver can launch and control Chrome locally.
- Added a reusable Pytest WebDriver fixture with automatic browser cleanup.
- Added and passed an initial browser smoke test.

### Key Decisions

- Selenium WebDriver and Pytest will provide external browser automation.
- The test repository will treat Job Search Hub as a black-box system under test.
- Selenium coverage will complement rather than duplicate lower-level application tests.
- Reliable local execution will be established before CI is introduced.
- Page Objects and other abstractions will be added where they provide demonstrated value rather than framework complexity for its own sake.

#### Additional Work Completed

- Added application support for an environment-selected database so external
  browser testing can use an isolated SQLite database rather than production
  application data.
- Verified the application-side change against the complete internal test suite:
  446 tests passed.
- Started Job Hub against an isolated Selenium test database and verified that
  the expected eight reference statuses were initialized.
- Confirmed the running application responds successfully at `http://127.0.0.1:5000`.
- Replaced the temporary browser test in the root `conftest.py` with a reusable
  Selenium WebDriver fixture in `tests/conftest.py`.
- Added the first external Job Hub Selenium smoke test.
- Verified the smoke test loads the Job Hub home page and validates both the
  expected page title and page content.
- Ran the complete external test suite successfully: 2 tests passed.

### Key Testing Decisions

- External Selenium tests will run against an isolated database rather than the
  normal Job Hub database.
- Browser lifecycle management belongs in reusable Pytest fixtures rather than
  individual functional tests.
- Basic Selenium/browser validation remains separate from Job Hub functional
  validation so infrastructure failures can be distinguished from application
  failures.

### Next Steps

- Add external Selenium coverage for the first meaningful Job Hub user workflow.
- Begin with creating a submitted job application through the UI.
- Expand traceability as functional Selenium coverage is added.
