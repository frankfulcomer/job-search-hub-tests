# Job Search Hub External Test Automation

## Purpose

This repository provides independent, black-box testing of
[Job Search Hub](../job-search-hub) through its externally observable user
interface: a real browser, driven by Selenium WebDriver, against a real
running instance of the application.

It implements the external automation portion of Job Search Hub's overall
Phase 1 test strategy (see `job-search-hub/docs/test-strategy.md`), and
exists to demonstrate practical Selenium WebDriver and Pytest test
automation, not to duplicate the application's own unit/integration/Flask
test suite.

## Repository separation

This repository is intentionally separate from `job-search-hub`:

- It does not import, or directly exercise, any Job Search Hub
  implementation code. It only drives the application through its HTTP/UI
  surface and, for verification, reads its SQLite database directly.
- It never touches the user's personal Job Search Hub data. Every test
  runs its own dedicated application process against a fresh, temporary,
  disposable SQLite database created for that test alone.
- Job Search Hub is expected to live in a sibling checkout
  (`../job-search-hub` relative to this repository) by default; see
  Configuration below for overriding that.

## Architecture and test lifecycle

For each application test, `tests/conftest.py`:

1. Picks a free local (loopback) TCP port and creates a fresh, empty
   SQLite file path under pytest's own `tmp_path`.
2. Starts Job Search Hub as a subprocess, via its own supported entry
   point (`flask run`, with `FLASK_APP=wsgi.py`), pointed at that database
   through the application's `JOB_HUB_DATABASE` environment variable, with
   the Flask debugger and reloader explicitly disabled.
3. Polls the new instance's home page until it responds (bounded by a
   startup timeout) before yielding control to the test. Ordinary
   application startup creates the schema and seeds reference statuses
   automatically - this repository never has to reset or prepare that
   database itself.
4. Tears the process down afterward unconditionally - on test success,
   test failure, or a setup error - terminating only the process this
   fixture started, never anything already running on the machine.

A single Chrome WebDriver instance (headless by default) is created once
per test session and reused across tests; it is quit at the end of the
session regardless of outcome.

Each application test therefore gets an isolated application instance and
an isolated, disposable database, while sharing one browser. Tests do not
depend on a manually started server and do not share state with each
other.

### Browser actions plus read-only SQL verification

Most assertions are made the way a real user would observe them: through
rendered page content. Where a scenario specifically claims persistence
correctness (e.g. "exactly one history record was created, with these
exact values"), tests additionally open the *same* fixture-owned SQLite
file directly, read-only (`sqlite3`, `file:...?mode=ro`), and query it with
explicit columns and joins.

This SQL step is a persistence oracle, not a shortcut: it never creates
test data or calls application business logic directly, and it never
connects to any database other than the one the current test's own
managed instance is using. It exists because passing UI assertions alone
can't distinguish "the page rendered the right thing" from "the database
actually holds the right relational data" - for example, that a status
change produced exactly one new `application_status_history` row linked
to the correct application, rather than, say, a display-only update.

Validation, boundary, and business-rule coverage that doesn't need a real
browser to verify meaningfully (e.g. exhaustive input-validation cases,
transaction-rollback behavior, timestamp precision) remains the
responsibility of `job-search-hub`'s own unit/integration/Flask test suite.
This repository does not attempt to re-prove that coverage.

## Prerequisites

- Python 3.14+ (matching the application's own `requires-python`).
- Google Chrome installed locally, with a browser/driver version Selenium
  Manager can resolve (verified below against Chrome 153.0.8010.52 with a
  matching cached `chromedriver`).
- A sibling `job-search-hub` checkout, with its own dependencies installed
  into its own virtual environment - concrete steps below, since
  `job-search-hub`'s own README does not currently document this. This
  repository does not install or vendor the application's code or schema;
  it only runs the application's existing, separately-installed
  environment as a subprocess.

## Setup

Both repositories need their own, separate virtual environment. Neither
installs into the other.

### 1. Application environment (`job-search-hub`)

```bash
cd ../job-search-hub   # sibling checkout, relative to this repository
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

`pip install -e ".[dev]"` is the same command `job-search-hub`'s own CI
workflow uses (`.github/workflows/ci.yml`) and installs, per its
`pyproject.toml`: the application itself in editable mode (so `flask run`
can `import job_hub`), its runtime dependency (Flask), and its `dev`
extra (pytest). No separate database-initialization step is needed - the
application creates its schema and seeds reference data automatically on
ordinary startup (see `job-search-hub/docs/decisions/
0001-phase-1-sqlite-persistence-foundation.md`).

Deactivate this environment (`deactivate`) before setting up this
repository's own, to avoid confusing the two.

### 2. Test environment (this repository)

```bash
cd ../job-search-hub-tests   # back to this repository
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

This repository's own dependencies are intentionally minimal: Selenium and
Pytest. It does not install Flask or anything else belonging to the
application - that lives entirely in `job-search-hub`'s own environment,
set up above. `tests/conftest.py` locates and runs that environment as a
subprocess (see Configuration below if it is not a sibling checkout).

### 3. Running the tests

```bash
source .venv/bin/activate   # this repository's own environment
pytest tests/
```

Useful options:

- `pytest tests/ --headed` - run with a visible Chrome window instead of
  headless, to watch a scenario execute.
- `pytest tests/test_status_history.py` - run a single scenario file.
- `pytest tests/ -v` - verbose per-test output.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `JOB_HUB_APP_DIR` | Path to the `job-search-hub` checkout to run. | `../job-search-hub` (sibling of this repository) |
| `JOB_HUB_PYTHON` | Python interpreter used to run the application subprocess. | `<JOB_HUB_APP_DIR>/.venv/bin/python` if it exists, else the interpreter running pytest |

Neither variable needs to be set for the default sibling-checkout layout
used during this milestone's development.

## Verified application revision

This milestone's scenarios were implemented and verified against
Job Search Hub commit `26a42ed` ("Support isolated database for external
testing"), the commit that added `JOB_HUB_DATABASE` support. That change
was required for this repository to run isolated from personal data and
was made and verified (446 passing application tests) before this
repository's scenarios were written; see
`job-search-hub/docs/journal/2026-09.md` for that work's own record.

## Implemented coverage

| Scenario | Test(s) | Requirement(s) |
| --- | --- | --- |
| Browser/application smoke | `test_job_hub_smoke.py` | FR-003 (home page reachable) |
| Pure browser/WebDriver smoke (no application dependency) | `test_browser_smoke.py` | - |
| Create and read an application, with SQL persistence verification | `test_create_application.py` | FR-001, FR-003, FR-005 |
| Required-field rejection (native browser validation), parameterized over company/title/source/date | `test_required_field_validation.py` | FR-011 |
| Server-side validation and recovery: whitespace-only required text, missing retrospective status time, compensation min > max; one resubmission demonstrated | `test_server_validation.py` | FR-011, FR-001 |
| Status change with later effective time, history preserved and ordered, with SQL persistence verification | `test_status_history.py` | FR-007, FR-005 |

See `docs/traceability.md` for the full, intentionally lightweight
requirement mapping, including requirements left explicitly deferred.

This is a focused first milestone, not exhaustive coverage. In particular,
it does not include: duplicate-warning override, editing, archive/restore,
search/filtering/sorting, pagination, or reference-data (company/source/
location) reuse scenarios. These are documented roadmap items, not gaps
discovered by accident.

## Design decisions

- **Pytest owns the application's lifecycle, not a manually started
  server.** A fixture starting and stopping its own subprocess, against
  its own disposable database, is what makes "run this repeatedly, in any
  order, with no shared state" true rather than aspirational.
- **One browser, many disposable application instances.** Launching Chrome
  is the slower, more failure-prone part of setup; reusing one instance
  per session while giving every test its own application process and
  database keeps tests isolated from each other without re-paying Chrome's
  startup cost per test.
- **Date and datetime-local inputs are set via JavaScript, not
  `send_keys`.** These native controls render a locale-sensitive picker
  widget rather than a plain text box, so keyboard input behavior is not
  reliable across locales or browser versions. `pages/dom.py` instead
  assigns the control's ISO value directly and dispatches the `input`/
  `change` events the page's own validation and form state depend on, then
  re-reads the value to confirm the browser actually accepted it. Actual
  submission still goes through the real "Save application"/"Save status
  change" button, so server-side handling and validation behavior are
  exercised normally. This means native date-picker *keyboard* interaction
  itself is not covered by these tests - an accepted, explicit limitation
  rather than an oversight.
- **Lightweight Page Objects, not a framework.** Each page object is a
  small class holding that page's locators and the handful of interactions
  tests actually use (`pages/`). Assertions themselves stay in the test
  files, not inside page objects, so a test's expected behavior is visible
  at the call site.
- **SQL verification opens the exact file the test's own instance is
  using, read-only.** Never a separately supplied path, and never anything
  resembling the user's personal database. See "Browser actions plus
  read-only SQL verification" above.
- **Fixed, past synthetic dates rather than "today" or random data.**
  Scenarios use explicit, comfortably-past dates and explicit initial
  status effective times throughout, so behavior doesn't depend on the
  real calendar date tests happen to run on, and so isolated, per-test
  databases don't need randomized data to avoid collisions with anything
  left over from a previous run.

## Limitations

- Native HTML date-picker keyboard interaction is not exercised (see
  "Design decisions" above); the resulting field *value* and subsequent
  form submission/validation are, through the real UI.
- No continuous integration workflow exists yet for this repository. This
  is an outstanding Phase 1 item, not a completed milestone claim - see
  `docs/test-strategy.md`.
- Browser/driver compatibility was verified locally against one specific
  Chrome version; cross-browser and cross-version coverage is out of scope
  for this milestone.
- Coverage is intentionally partial - see "Implemented coverage" above and
  `docs/traceability.md`.

## Troubleshooting

- **A test fails during `app_server` fixture setup, before any browser
  interaction.** This is almost always environment-related, not a product
  defect: check that `JOB_HUB_APP_DIR` resolves to a real `job-search-hub`
  checkout with its own dependencies installed, and that nothing else is
  already bound to the port pytest happened to choose (rare, since the
  port is freshly selected per test).
- **Chrome fails to start at all.** Confirm Google Chrome is installed and
  that Selenium Manager can resolve a matching `chromedriver` (it caches
  one under `~/.cache/selenium`); this surfaces as a `driver` fixture setup
  error, distinct from any test's own assertions.
- **A test fails after the application and browser both started
  successfully.** This is a product-behavior or test-expectation mismatch,
  not an environment problem - the fixtures above exist specifically to
  make that distinction possible.
- **Watching a failure interactively:** rerun with `--headed` and, if
  useful, a single test selected by its node id.

## Roadmap

Documented as future work, not implied by this milestone:

- Duplicate-application warning and override.
- Edit-application workflow.
- Archive and restore.
- Search, filtering, sorting, and pagination.
- Reference-data (company/source/location) reuse and suggestion behavior.
- Continuous integration running this suite against a known application
  revision in an isolated environment.

## AI assistance

Implementation (fixtures, page objects, test scenarios, this
documentation) was written by Claude (Anthropic), working from an
implementation brief prepared by Codex (OpenAI) under human product
direction. Codex reviewed that initial implementation and independently
ran the external suite, verifying 11 browser tests passing in 17.30
seconds - a separate run from any of Claude's own reported results below
- and requested the focused corrections recorded in `docs/test-journal.md`
("Review Follow-Up"). Final review and human approval are still pending as
of this revision. Test execution, failure investigation, and the
verification evidence recorded in `docs/test-journal.md` were performed
directly against a real running application instance and a real browser,
not simulated or asserted from memory.
