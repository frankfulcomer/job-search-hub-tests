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

## 2026-10-04 - Transcript Preservation and Companion Highlights

A full session transcript, exported via `/export` to this repository's
root as `2026-10-04-122503-document-repository-privacy-audit-and-lessons-lea.txt`,
covered three tasks: privacy-audit documentation work performed in the
sibling `job-search-hub` repository (already fully recorded there as commit
`50e1b68` plus that repository's own journal and lessons-learned entries),
this milestone's implementation (recorded above), and Codex's review
findings and Claude's corrections (recorded above). The export was
untracked and contained personal information: an account email address and
several local home-directory paths.

### Private preservation

Computed the export's SHA-256 checksum, copied it unchanged to
`~/Private/job-search-hub-transcripts/` (a location outside both
repositories' working trees), and confirmed the copy was byte-for-byte
identical to the original via both a checksum comparison and `cmp` before
removing the original from this repository's working directory. The
original was not committed, and no Git history was rewritten - it was
simply never added to the index in the first place. A short manifest note
was left alongside the private copy (also outside both repositories)
recording its origin and the sanitized file it corresponds to.

### Sanitization

Determined, from the transcript's own content (its sequence of `❯` prompts,
not filenames or assumptions), the exact line ranges for each of the three
tasks above. Prepared a sanitized copy, from the verified private original,
at `docs/transcripts/2026-10-04-privacy-audit-documentation-and-selenium-milestone.txt`
- the first transcript committed to this repository (`job-search-hub`'s
`docs/transcripts/` structure and naming convention was followed, newly
established here rather than extended there).

Identified every instance of personal information by direct inspection and
targeted search (not assumed from the single prior redaction precedent)
before changing anything: one occurrence of the account's first name (the
banner greeting), one occurrence of the account email address, and four
occurrences of an absolute `/home/<user>/...` path inside the human's own
prompt text. Also explicitly checked for and found none of: machine
identifiers beyond the home-directory username, credentials, tokens,
private key material, or phone-number-shaped strings.

Redacted the email address to the same `user@example.com` placeholder
`job-search-hub`'s own prior sanitized transcript already established
(copied that transcript's equivalent banner line verbatim, since both
sessions share identical Claude Code banner formatting apart from the
email and working-directory fields), and rewrote each absolute
home-directory path to its `~/...`-relative equivalent, consistent with
how this same transcript's own Claude Code banner already displays its
own working directory.

The banner greeting's first name was initially left unredacted in this
transcript, on the reasoning that it matched an established precedent in
`job-search-hub`'s own sanitized canonical transcript, which treats the
account's first name - unlike its email address and filesystem paths - as
not requiring redaction. On review, that precedent does not override this
task's redaction requirement for personal information generally: a
person's first name is itself personal information, regardless of an
earlier, separate transcript's treatment of it. The greeting was corrected
to replace the name with a neutral five-character placeholder ("there"),
chosen so the surrounding box-drawing layout's column width did not need
to be recalculated. `job-search-hub`'s own, already-committed canonical
transcript was not revisited or changed - that would require rewriting
that repository's Git history, which is out of scope here - so this
transcript now redacts the first name while that earlier, unrelated
transcript still does not; this inconsistency between the two is noted
here rather than silently left unexplained.

Verified the result by diffing the sanitized file against the verified
private original: confirmed the only differences were six intended
substitutions (the name, the email address, and the four path
occurrences), that every other line was byte-for-byte identical, and that
the line count was unchanged (2,798 lines in both). Re-scanned the
sanitized file afterward for the account's name, name-derived strings,
email domain, literal `/home/` paths, and common credential/token/
private-key patterns: no remaining matches. Also re-confirmed, by checksum
and `cmp`, that the private original at
`~/Private/job-search-hub-transcripts/` remained byte-for-byte unchanged
throughout this correction.

### Overlap handling

The transcript's first task (privacy-audit documentation in
`job-search-hub`) is not separately summarized or duplicated in this
repository: it is already fully recorded in `job-search-hub` itself (commit
`50e1b68` and that repository's own `docs/journal/2026-09.md` and
`docs/lessons-learned.md`). `job-search-hub` was not modified by this
documentation pass - no reciprocal pointer was added there, since the
overlap is fully documented from this side (this entry and the companion
highlights document's "Scope and provenance" section both name the
specific commit and files involved) and touching an already-committed,
already-pushed repository for a cross-reference alone was judged
unnecessary. The full transcript lives in exactly one place
(`job-search-hub-tests`), not copied into both repositories.

### Companion highlights

Located `job-search-hub`'s existing companion highlights document
(`docs/transcripts/2026-09-20-to-2026-09-23-phase-1-highlights.md`) before
writing anything, to decide whether to extend it. Its stated coverage is
the Phase 1 application MVP effort in the other repository - a different
repository, phase, and test level from this milestone - so extending it
would have mixed two repositories' records into one document. Created a
new, clearly-identified companion instead:
`docs/transcripts/2026-10-04-selenium-milestone-highlights.md`, scoped to
this transcript's second and third tasks only (the first being
`job-search-hub`'s own, as above). It links to the sanitized transcript and
to this journal, distinguishes human direction, Codex's brief and
independent review, and Claude's implementation and corrections, and
records the meaningful correction found along the way (the earlier,
disproven "missing application date" hypothesis) rather than presenting
an artificially clean narrative. Milestone commit `275c700` was verified
present on `main` via `git log`/`git show` before being cited.

Results recorded with their correct provenance: Codex's own, independently
run 11-passed-in-17.30-seconds figure is distinguished throughout from
Claude's separate runs (15.67s/14.42s/14.33s and the individual runs,
recorded above); the 446-passing application-suite figure remains
attributed to Claude's run only. The highlights document explicitly states
that Codex's final review of the correction pass, and human approval, had
not yet occurred as of the end of the transcript it describes.

### Verification

```
$ git diff --check
```
No output (no whitespace errors).

```
$ git status --short
```
Showed only this documentation pass's own new/modified files
(`docs/transcripts/2026-10-04-privacy-audit-documentation-and-selenium-milestone.txt`,
`docs/transcripts/2026-10-04-selenium-milestone-highlights.md`, this
journal) - no trace of the raw export (relocated out of the repository
before this check) and no generated database, report, screenshot, or log
file. Re-scanned every newly added file for credential/token/private-key
patterns, stray email addresses, and `/home/` paths: none found beyond the
single intentionally-preserved greeting noted above (see "Correction:
Codex's Review of This Documentation Pass" below - that greeting was
subsequently redacted too).

This was a documentation-only task: no application code, test code, or
test coverage was changed, so the external suite was not re-run as part of
it. Not committed, tagged, or pushed. Ready for Codex's review and human
approval, alongside the correction pass recorded above.

### Correction: Codex's Review of This Documentation Pass

Codex reviewed the transcript and highlights work above and requested
three focused corrections:

1. **Incomplete redaction.** The banner greeting's first name should be
   redacted like the email address and paths were, regardless of the
   unrelated precedent in `job-search-hub`'s own, separate, already-
   committed transcript.
2. **Mixed chronology.** The highlights document's final section mixed
   what the transcript itself records (ending with Claude's correction
   report) with events that happened afterward, outside the transcript
   (Codex's subsequent confirmation and the human's commit action),
   without clearly separating the two or attributing the latter to their
   actual source.
3. **Missing working links.** Plain-text filename references to the
   sanitized transcript and to this journal should be working relative
   Markdown links, checked to actually resolve.

Each was corrected:

1. Replaced the personalized greeting with a neutral greeting in the
   sanitized transcript (a same-length placeholder chosen so nothing else on that line needed re-padding), and rewrote the "Sanitization" section above to explain the correction and why the earlier precedent does not apply here. Re-confirmed the private original at
   `~/Private/job-search-hub-transcripts/` was unchanged (checksum and
   `cmp`, both still matching the value recorded earlier in this entry),
   and re-diffed the sanitized file against it: exactly six differences
   now (the name, the email, and the four path occurrences), every other
   line byte-for-byte identical, line count still 2,798/2,798.
2. Rewrote the highlights document's final section (now "6. Chronology:
   Transcript End and Subsequent Events") into four explicit parts: what
   the transcript itself shows at its end; what is known to have happened
   afterward, attributed to the supplied Codex review context and to Git
   evidence rather than to the transcript; the specific Git evidence
   (commit `275c700`, re-verified locally); and the current, still-
   uncommitted state of this documentation pass itself. The transcript
   file itself was not touched to add any of this.
3. Added working relative Markdown links from the highlights document to
   the sanitized transcript (`2026-10-04-privacy-audit-documentation-and-selenium-milestone.txt`,
   a same-directory sibling) and to this journal (`../test-journal.md`),
   at every plain-text mention of either file. Verified both relative
   paths resolve with `realpath -e` from the highlights document's own
   directory.

Re-verification: `git diff --check` reported no whitespace errors. `git
status --short` showed only `docs/test-journal.md` (modified) and
`docs/transcripts/` (containing the two files already recorded above) -
no other file. Re-scanned both files in `docs/transcripts/` again for the
account's name, name-derived strings, email domain, literal `/home/`
paths, and credential/token/private-key patterns: no matches of any kind
remained. No application or test code was touched; the external suite was
not re-run, consistent with this remaining a documentation-only task.
Still not committed, tagged, or pushed. Ready for Codex's review and human
approval.
