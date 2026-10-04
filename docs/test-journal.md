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

## 2026-10-04 - First Focused Testing Milestone: Fixtures, Scenarios, and Verification

Implemented from a Codex-prepared implementation brief under human product
direction, per the working model recorded in
`job-search-hub/docs/development-process.md`: the human sets direction,
Codex prepares implementation instructions and independently reviews and
verifies the result, Claude writes the implementation.

### Incorporating Prior Uncommitted Work

Two pieces of uncommitted work existed at the start of this task and were
carried forward rather than discarded:

- The `test_create_application` test added directly to
  `tests/test_job_hub_smoke.py` (filling company, title, and source, then
  asserting the list page) established the right workflow and intent -
  creating an application through the real UI and checking the result.
  Its intent is preserved and substantially expanded in
  `tests/test_create_application.py`: the richer version also supplies
  application date and initial status time (both required for a
  non-trivial, retrospective-safe scenario), verifies the detail page, and
  adds read-only SQL verification of the underlying `application`,
  `company`, `source`, and `application_status_history` rows.
  `tests/test_job_hub_smoke.py` itself now holds only the browser/
  application smoke scenario (home page reachable), since the create
  workflow it originally held moved to its own, more thorough test module.
- `scripts/reset_test_db.py` predated pytest-owned fixtures and reset a
  fixed, dedicated Selenium database file directly. Its role is now
  superseded by `tests/conftest.py`'s `app_server`/`app_db` fixtures,
  which give every test its own fresh, pytest-`tmp_path`-owned database
  automatically. The script was not deleted; it was kept and re-documented
  (see its module docstring) as an optional, manual, non-automated utility
  for ad-hoc local exploration, with its existing safety property made
  explicit: it only ever touches its own dedicated filename, never the
  personal database, and never a path from an argument or environment
  variable.

### Inspection Findings Carried Into Implementation

- Confirmed the application date field defaults to today (via the "New
  Application" form's `today` template variable), not a missing default
  as an earlier hypothesis suggested; this was not established as a cause
  of any prior failure and is not treated as a defect here.
- Confirmed `JOB_HUB_DATABASE` (added in application commit `26a42ed`)
  works exactly as needed: pointed at a fresh path, ordinary application
  startup creates schema and seeds the eight reference statuses without
  requiring any manual reset step.
- Confirmed, by reading `src/job_hub/applications.py` and the create-
  application route/template, that a retrospective initial status (any
  application date other than today, with the default `APPLIED` status)
  requires an explicit initial status effective time, and that this is
  enforced server-side (`initial_status_effective_at` carries no HTML
  `required` attribute) rather than blocked by native browser validation.
  This distinction shaped `test_server_validation.py`.

### Implementation

- `tests/conftest.py`: added `pytest_addoption` (`--headed`), a session-
  scoped `driver` fixture (headless by default), a function-scoped
  `app_server` fixture (free loopback port, fresh `tmp_path` SQLite file,
  `flask run` subprocess with reloader/debugger disabled, bounded
  readiness polling, unconditional teardown that terminates only the
  process it started), and a function-scoped `app_db` fixture (read-only
  `sqlite3` connection to that exact database file).
- `pages/`: `dom.py` (shared JS-based date/datetime-local value assignment
  and native-validity check), `home_page.py`, `new_application_page.py`,
  `application_list_page.py`, `application_detail_page.py`,
  `status_change_page.py`. Each is a small class holding that page's
  locators and interactions; assertions remain in the test files.
- `tests/test_browser_smoke.py`: refactored to use the shared `driver`
  fixture and removed the three-second `sleep`, while keeping its
  deliberately application-independent purpose (pure WebDriver/Chrome
  capability) unchanged.
- `tests/test_job_hub_smoke.py`, `tests/test_create_application.py`,
  `tests/test_required_field_validation.py`,
  `tests/test_server_validation.py`, `tests/test_status_history.py`: the
  six scenario families from the implementation brief's scope table.
- `tests/support.py`: shared UI-creation helper and the independently
  reproduced (not imported) persisted-timestamp format from ADR 0001, used
  to compute expected SQL values.
- No `requirements.txt` change: no new test dependency was needed (free-
  port selection, subprocess management, HTTP readiness polling, and
  read-only SQL verification all use the standard library already
  available via `selenium`/`pytest`'s own dependencies).
- No Job Search Hub application changes were made or were found to be
  needed; `26a42ed` already provided everything this milestone required.

### Verification (freshly run 2026-10-04)

External suite, first clean run:

```
$ pytest tests/ -v
11 passed in 15.67s
```

All eleven tests passed on the first run with no failures to investigate
or fix.

Rerun, confirming repeatability:

```
$ pytest tests/ -v
11 passed in 14.42s
```

Reordering, confirming order independence (file order reversed from the
default collection order):

```
$ pytest tests/test_status_history.py tests/test_server_validation.py \
    tests/test_required_field_validation.py tests/test_job_hub_smoke.py \
    tests/test_create_application.py tests/test_browser_smoke.py -v
11 passed in 14.33s
```

Individual execution, confirming no cross-test dependency, run separately
for one file or test from each scenario family (`test_browser_smoke.py`,
`test_job_hub_smoke.py`, `test_create_application.py`,
`test_status_history.py`,
`test_required_field_validation.py::...[company_name]`,
`test_server_validation.py::test_compensation_min_above_max_is_rejected`):
all passed individually, in 0.85s-3.43s each.

`git status` in both repositories showed no new tracked or untracked
database, report, screenshot, or log files after any of the above runs -
only the source files this milestone intentionally added or modified.
`git status` in `job-search-hub` (the application repository) remained
completely clean throughout. That establishes that no file Git already
tracks there was modified; it does not, by itself, establish that no
ignored or untracked file (for example, a transient SQLite file under
`src/instance/`) was touched, since `git status` does not report changes
to paths matched by `.gitignore`. Database isolation is established
instead by the fixture configuration actually used: `tests/conftest.py`'s
`app_server` fixture sets `JOB_HUB_DATABASE` explicitly to a path under
pytest's own `tmp_path` for every test, never to any path under
`job-search-hub/src/instance/` - so the application process this suite
starts has no occasion to read, create, or write anything inside that
repository's instance directory in the first place. This was not
separately confirmed by inspecting `job-search-hub/src/instance/` during
this run (doing so was out of scope and unnecessary given the explicit
`JOB_HUB_DATABASE` configuration).

Environment versions verified at the same time: Python 3.14.4, Selenium
4.49.0, pytest 9.1.1, Google Chrome 153.0.8010.52 with a matching cached
`chromedriver` 153.0.8010.52 (no network download needed).

Application revision verified against: `26a42ed` ("Support isolated
database for external testing"), working tree clean.

Claude also re-ran the application's own full suite directly, to report a
figure freshly verified during this implementation task rather than
reusing the 446-passing count recorded historically in
`job-search-hub/docs/journal/2026-09.md`:

```
$ pytest -q   # run from job-search-hub, no application changes made
446 passed in 12.63s
```

This run was performed by Claude, not independently reproduced by Codex;
Codex's own independent verification of this milestone (11 browser tests
passing in 17.30 seconds) covered the external suite only, not a rerun of
the application's own test suite.

### Gaps and Human/AI Roles

- Coverage is intentionally partial; see README.md "Implemented coverage"
  and "Limitations", and `docs/traceability.md`. Duplicate-warning
  override, edit, archive/restore, search/filter/sort/pagination, and
  reference-data reuse scenarios are deferred, not accidentally omitted.
  Native date-picker keyboard interaction is not exercised (see
  `pages/dom.py`'s docstring).
- No CI workflow was added; this remains an outstanding Phase 1 item.
- Direction: human (product scope, working model, repository boundaries).
  Implementation instructions, independent review, and result
  verification: Codex, from the implementation brief this milestone
  follows. Fixtures, page objects, test scenarios, and documentation:
  Claude. All verification evidence recorded above was produced by
  actually running the suite against a real browser and a real
  application instance, not asserted from the implementation brief or
  from memory.

## 2026-10-04 - Review Follow-Up: Codex's Findings on the First Milestone

Codex reviewed the implementation recorded above and independently ran the
external suite: **11 passed in 17.30 seconds** - a separate run from any
of Claude's reported results above, consistent with them but not the same
measurement. The application repository's Git working tree remained clean
during Codex's run as well; per the correction below, that is evidence
consistent with database isolation, not proof of it on its own. Codex's
verdict: the core implementation needs no redesign. Codex requested three
focused corrections, addressed here by Claude. **Final review and human
approval remain pending** as of this entry.

### 1. Incomplete README setup instructions

`README.md`'s "Prerequisites" previously pointed readers to
`job-search-hub`'s "own setup instructions" for installing the
application - but that repository's README does not actually document
any install steps. `README.md`'s "Setup" section now gives concrete,
numbered steps for both sibling repositories' separate virtual
environments: `job-search-hub`'s own (`pip install -e ".[dev]"`, matching
`.github/workflows/ci.yml` and installing per its `pyproject.toml`: the
application itself editable, Flask, and the `dev` extra's pytest) and this
repository's own (`pip install -r requirements.txt`), followed by running
the suite.

Verified by installing `job-search-hub` with exactly that command into a
disposable, throwaway virtual environment (not the existing working one)
and confirming `import job_hub`, `import flask`, `import pytest`, and
`flask --help` (with `FLASK_APP=wsgi.py`) all succeeded, then discarding
that environment.

### 2. `.gitignore` did not cover local secrets or generated database/log files

Before changing anything, confirmed no file matching the patterns below
was already tracked (`git ls-files | grep -iE '\.env|\.sqlite|\.db$|\.log$|...'`)
and that none was present untracked on disk outside `.venv/` either - so
nothing was being newly hidden by this change.

Added to `.gitignore`: `.env` / `.env.*` (with `!.env.example` preserved,
matching the same publishable-example convention `job-search-hub`'s own
`.gitignore` uses), `*.sqlite` / `*.sqlite3` and its `-wal`/`-shm`/
`-journal` sidecar files, `*.db`, and `*.log`. This repository's own test
databases are always created under pytest's `tmp_path`, outside the
repository entirely, so these patterns are a safety margin rather than a
response to an actual leak.

Verified with `git check-ignore -v` against representative filenames for
every new pattern (`.env`, `.env.local`, a `*.sqlite3` file and its three
sidecar suffixes, a `*.db` file, a `*.log` file) - all ignored - and
separately confirmed `.env.example` is *not* ignored (the negation pattern
is the last matching rule for it).

### 3. Documentation and verification provenance corrections

- **`README.md` "AI assistance"**: replaced the claim that Codex had
  already "reviewed the resulting diff and verified the implementation
  against that brief before human approval" - stated as settled fact -
  with an accurate account: Codex reviewed the initial implementation,
  independently verified 11 browser tests passing in 17.30 seconds, and
  requested the corrections recorded in this entry. Final review and
  human approval are explicitly noted as still pending.
- **446-passing application-suite figure**: the "Verification" section
  above now attributes that fresh run explicitly to Claude and states
  plainly that Codex has not independently rerun the application's own
  suite - only the external suite, which is what Codex's own 11-passed
  figure reflects.
- **Git-status/isolation claim**: the "Verification" section above
  previously stated that a clean `git status` in `job-search-hub`
  "confirm[ed] the external suite never touched anything under that
  repository." That overstated what `git status` actually shows: it
  reports tracked-file changes, not changes to paths `.gitignore` already
  excludes, so a clean status cannot by itself rule out an ignored file
  being touched. The claim was rewritten to rely on the actual evidence
  available instead: `tests/conftest.py`'s `app_server` fixture sets
  `JOB_HUB_DATABASE` explicitly to a path under pytest's `tmp_path` for
  every test, never to any path under `job-search-hub/src/instance/`, so
  the application process this suite starts has no occasion to read or
  write anything inside that repository's instance directory in the first
  place. This entry does not claim that directory was separately
  inspected to confirm it, since doing so was not necessary given the
  explicit configuration and was out of scope for this follow-up (per the
  original brief's privacy-audit guidance: do not read personal database
  contents).
- This entry itself: added to preserve Codex's findings and their
  resolution as part of the project record, without altering the original
  2026-10-04 implementation entry above (its role-description language
  describing Codex's place in the working model was left as originally
  written, since it describes the process rather than asserting this
  specific review had already concluded).

### Scope of this follow-up

No application code was changed. No test coverage was added, removed, or
altered - the correction scope was limited to `README.md`, `.gitignore`,
and this journal, exactly as Codex's findings specified. No executable
(`.py`) file was touched, so the external suite's behavior could not have
changed; it was re-run anyway as a sanity check (see below) rather than
assumed unaffected.

### Verification

```
$ git diff --check
```
No output (no whitespace errors introduced).

```
$ pytest tests/ -v
11 passed in 15.18s
```

Re-run as a sanity check, not because any executable file changed - all
eleven tests passed again, matching both Claude's original runs and
Codex's independent 17.30-second run.

Still pending: Codex's final review of these corrections, and human
approval. Not committed, tagged, or pushed.
