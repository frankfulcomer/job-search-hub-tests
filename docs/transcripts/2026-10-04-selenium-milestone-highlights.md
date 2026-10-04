# Job Search Hub Tests — First External Testing Milestone Highlights

**Coverage:** 2026-10-04 — implementation of the first focused external
testing milestone and Codex's review correction pass.
**Source of record:** [`docs/transcripts/2026-10-04-privacy-audit-documentation-and-selenium-milestone.txt`](2026-10-04-privacy-audit-documentation-and-selenium-milestone.txt)
(sanitized session transcript). This document covers only that transcript's
second and third tasks (lines 776 onward); see "Scope and provenance" below
for why its first task is out of scope here.
**Milestone commit:** `275c700` ("Add isolated Selenium workflow tests with
SQL verification"), verified present on this repository's `main` at the time
this document was written.

This document is derived from that transcript, from
[`docs/test-journal.md`](../test-journal.md), and from this repository's
Git history. It is a secondary, human-readable
artifact and does not replace the transcript, the journal, the application
repository's own requirements/architecture/journal documentation, the test
suite, or Git history. Where this document and the transcript appear to
disagree, the transcript governs.

## Scope and provenance

The source transcript is one continuous Claude Code session that happens to
cover three separate tasks, the first in a different repository:

1. **Lines 1–775:** documenting a privacy/security audit of the sibling
   `job-search-hub` application repository ahead of its public release —
   authoring its `docs/journal/2026-09.md` "Privacy and Public Release
   Preparation" journal entry and `docs/lessons-learned.md` additions,
   revising them per feedback, committing (`job-search-hub` commit `50e1b68`,
   "Document repository privacy audit and lessons learned"), pushing, and
   running a read-only pre-publication release gate.
2. **Lines 776–2189:** implementing this milestone (below).
3. **Lines 2190–2798:** Codex's review of that implementation and Claude's
   corrections (below).

Task 1 belongs entirely to `job-search-hub`, is already fully recorded there
(the commit above, plus that repository's own journal and lessons-learned
entries), and is not summarized in this document — doing so here would
duplicate, in a different repository, a record that repository already owns.
For the same reason, the full transcript is preserved once, in this
repository, rather than copied into both; `job-search-hub` was not otherwise
modified by this documentation pass. The raw, unredacted export (containing
an account email address and local home-directory paths) is preserved
privately outside both repositories' working trees, not committed to either.

This document itself is new rather than an extension of
`job-search-hub/docs/transcripts/2026-09-20-to-2026-09-23-phase-1-highlights.md`:
that document is explicitly scoped to the Phase 1 application MVP effort in
the other repository, and tasks 2–3 here belong to a different repository,
a different and later milestone, and a different test level (external
browser/SQL verification rather than application implementation). Extending
it would have mixed two repositories' and two phases' records into one
document; a clearly-identified, separate companion was judged the better
fit, consistent with the application repository's own guidance that
highlights are a secondary artifact per canonical transcript, not a single
running summary of everything.

---

## 1. Human Direction and Working Model

Direction for this milestone came from a human-authored implementation
brief request, under an explicit three-way working model stated directly in
the session: *"I provide product direction, Codex prepares implementation
instructions and independently reviews/verifies your work, and you write
the code."* The human also set firm boundaries up front and reiterated them
at each step: no commit, tag, push, publish, remote CI trigger, or Git
history rewrite without explicit approval; keep the two repositories
separate; keep the implementation small and understandable; report evidence
and a proposed minimal fix rather than silently expanding scope if an
application change turned out to be needed.

## 2. Codex's Implementation Brief and Review

Codex's brief (`~/Documents/Codex/2026-10-04/referenced-chatgpt-conversation-this-is-an/outputs/claude-implementation-brief.md`)
specified, among other things: pytest-owned application/database lifecycle
fixtures; a single reusable Chrome fixture; five focused scenario families
(browser/application smoke; create and read an application; required-field
rejection; server validation and recovery; status/history) with specific
required evidence for each; a read-only SQL verification oracle opened
against the exact fixture-owned database; README/traceability/strategy/
journal documentation requirements; and a privacy/secrets/generated-artifact
audit. The brief also recorded its own inspection findings to prevent
repeating earlier hypotheses as confirmed fact — notably: *"Contrary to the
earlier conversation's hypothesis, the application date input currently
defaults to today. A missing date was not established as the previous
failure's cause."* Claude's implementation treated this as a correction to
carry forward, not a finding to silently drop.

After Claude's implementation, Codex reviewed it and **independently ran the
external suite: 11 passed in 17.30 seconds**, with the application
repository's own Git working tree remaining clean during that run. Codex's
verdict was that the core implementation needed no redesign, but requested
three focused corrections:

1. `README.md`'s setup instructions referred readers to `job-search-hub`'s
   "own setup instructions" for installing the application — instructions
   that repository's README does not actually contain.
2. `.gitignore` did not cover local secret/environment files, SQLite
   databases and their sidecar files, or loose logs.
3. Documentation and verification provenance needed correction in three
   places: a premature claim that Codex's review had already concluded
   before human approval; an application-suite pass-count that needed
   clear attribution to Claude rather than Codex; and a journal claim that a
   clean `git status` in `job-search-hub` proved the external suite never
   touched anything there, which overstates what `git status` actually
   shows.

**Final review and human approval of Claude's corrections below remain
pending as of the end of this transcript.** (See
[Section 6](#6-chronology-transcript-end-and-subsequent-events) for what is
known to have happened after this transcript ends, from sources other than
the transcript itself.)

## 3. Claude's Implementation

### Repository separation and application/database isolation

`job-search-hub-tests` imports no application implementation code. Each
application-level test gets its own dedicated `job-search-hub` subprocess,
started via the application's own supported entry point (`flask run`, with
`FLASK_APP=wsgi.py`, debugger and reloader explicitly disabled) on a freshly
selected loopback port, pointed at a fresh SQLite file created under
pytest's own `tmp_path` through the application's existing `JOB_HUB_DATABASE`
environment variable. Ordinary application startup then creates schema and
seeds reference statuses automatically — this repository never resets or
prepares that database itself, and never points at anything under
`job-search-hub/src/instance/`. Readiness is established by bounded polling
of the new instance's home page rather than a fixed delay. The process,
its database connection, and the browser session are all released on test
success, test failure, and fixture setup error alike; a fixture only ever
terminates the process it itself started. A single Chrome WebDriver instance
(headless by default, `--headed` available) is created once per test session
and reused across tests, while every test still gets its own isolated
application instance and database.

### Lightweight Page Objects

`pages/` holds one small class per page (`home_page.py`,
`new_application_page.py`, `application_list_page.py`,
`application_detail_page.py`, `status_change_page.py`), each owning that
page's locators and the handful of interactions tests actually use, plus a
shared `dom.py` helper — deliberately not a generalized automation
framework. Assertions remain in the test files rather than inside page
objects, so each test's expected behavior is visible at its call site.

### Browser actions plus read-only SQL verification

Most assertions observe the application the way a user would: rendered page
content. Where a scenario specifically claims a persistence outcome (e.g.,
"exactly one history record was created, with these exact values"), the
test additionally opens the *same* fixture-owned SQLite file directly,
read-only (`sqlite3`, `file:...?mode=ro`), and verifies it with explicit
columns and joins — a persistence oracle, never a way to create test data or
call application logic directly. This exists because UI assertions alone
cannot distinguish "the page rendered the right thing" from "the database
actually holds the right relational data." Detailed validation, boundary,
transaction-rollback, and timestamp-precision coverage that doesn't need a
real browser to verify meaningfully remains the responsibility of
`job-search-hub`'s own unit/integration/Flask test suite; this repository
does not attempt to re-prove that coverage.

### Native versus server-side validation

Required-field omission (company, title, source, application date) is
blocked by the browser's own HTML constraint validation before any request
reaches the server — verified by checking the field's native validity and
that the URL never changed, with SQL confirming zero rows were written
across every relevant table. This is distinct from values the browser lets
through but the application itself must still reject: whitespace-only
required text, a missing initial status effective time on a retrospective
entry, and minimum compensation above maximum all produce a field-specific
server error, with valid input the user already entered preserved rather
than lost, and no partial writes. One case (the whitespace-only field) also
demonstrates correcting the invalid value and resubmitting successfully.

### Retrospective-date reasoning

Reading `src/job_hub/applications.py` and the create-application
route/template directly (rather than assuming from memory) confirmed that
an initial status of `APPLIED` defaults its effective time only when the
application date is today; any other application date (a retrospective
entry) requires an explicit initial status effective time, enforced
server-side rather than by any HTML `required` attribute. Every scenario
therefore uses fixed, comfortably-past synthetic dates with an explicit
initial status effective time supplied, rather than "today," so behavior
never depends on the real calendar date a run happens to execute on.

### Status/history

Creating an application and then recording a later-effective `SCREENING`
status change (with notes) is verified to update the current status
everywhere it is displayed (detail and list), while the original `APPLIED`
history entry remains intact and both entries appear in ascending
chronological order. SQL verification confirms exactly two
`application_status_history` rows for that application, with the correct
status names, effective timestamps, notes, and both linked to the same
application.

### Incorporating prior uncommitted work

Two pieces of work already existed, uncommitted, before this milestone and
were carried forward rather than discarded: an inline create-application
test in `tests/test_job_hub_smoke.py`, whose intent was preserved and
substantially expanded into its own `tests/test_create_application.py`
(adding application date, initial status time, detail-page verification,
and SQL verification); and `scripts/reset_test_db.py`, a manual database
reset script predating pytest-owned fixtures, which was kept (not deleted)
and re-documented as an optional, non-automated utility now superseded by
the `app_server`/`app_db` fixtures, with its existing safety property (it
only ever touches its own dedicated filename) made explicit.

### Verification (Claude's runs)

First clean run: **11 passed in 15.67s**. Rerun: **11 passed in 14.42s**.
Reordered (file order reversed): **11 passed in 14.33s**. Individually, one
test or file from each scenario family: all passed, 0.85s–3.43s each.
`git status` showed no new tracked or untracked database, report,
screenshot, or log file after any run, in either repository. Environment
versions recorded at the time: Python 3.14.4, Selenium 4.49.0, pytest 9.1.1,
Google Chrome 153.0.8010.52 with a matching cached `chromedriver`
153.0.8010.52. Application revision verified against: `26a42ed` ("Support
isolated database for external testing"). Claude also re-ran the
application's own full suite directly: **446 passed in 12.63s** — this
figure is Claude's own fresh run, reported as such and distinct from the
446-passing count recorded historically in `job-search-hub`'s own 2026-09
journal; Codex did not independently reproduce it.

## 4. Codex's Review Findings and Claude's Corrections

Addressing the three findings from Section 2:

1. **README setup instructions:** rewritten with concrete, numbered steps
   for both sibling repositories' separate virtual environments —
   `pip install -e ".[dev]"` for `job-search-hub` (confirmed identical to
   that repository's own `.github/workflows/ci.yml`) and
   `pip install -r requirements.txt` for this repository — verified by
   installing the application with exactly that command into a disposable,
   throwaway virtual environment and confirming `import job_hub`, `flask`,
   and `pytest` all succeeded, then discarding that environment.
2. **`.gitignore`:** before changing anything, confirmed no file matching
   the new patterns was already tracked or present untracked on disk.
   Added `.env`/`.env.*` (with `!.env.example` preserved, matching
   `job-search-hub`'s own convention), SQLite databases and their
   `-wal`/`-shm`/`-journal` sidecar files, `*.db`, and `*.log`. Verified
   every new pattern with `git check-ignore -v` against representative
   filenames, and separately confirmed `.env.example` is correctly *not*
   ignored.
3. **Documentation/verification provenance:** `README.md`'s "AI assistance"
   section no longer states that Codex's review had already concluded
   before human approval — it now states plainly that Codex reviewed the
   initial implementation, independently verified 11 browser tests passing
   in 17.30 seconds, and requested these corrections, with final review and
   human approval explicitly noted as still pending. The 446-passing
   application-suite figure in [`docs/test-journal.md`](../test-journal.md) is now explicitly
   attributed to Claude's own run, with a note that Codex has not
   independently rerun that suite. The journal's git-status claim was
   rewritten to rely on the fixture configuration actually used
   (`JOB_HUB_DATABASE` always pointed at a path under pytest's `tmp_path`,
   never under `job-search-hub/src/instance/`) rather than treating a clean
   `git status` as proof that nothing under `job-search-hub` was touched —
   since `git status` reports tracked-file state, not changes to
   `.gitignore`-excluded paths.

Verification after these corrections: `git diff --check` reported no
whitespace errors; the external suite was re-run as a sanity check (not
because any executable file had changed) and passed again, **11 passed in
15.18s** and, on a later re-check, **11 passed in 15.52s**. All of this
milestone's changes — implementation and corrections together — are present
in `job-search-hub-tests` commit `275c700`.

## 5. Deferred Coverage and Outstanding Work

Deliberately out of scope for this milestone, documented as roadmap items
rather than accidental gaps: duplicate-application warning/override, the
edit-application workflow, archive/restore, search/filtering/sorting/
pagination, and reference-data (company/source/location) reuse scenarios.
Native HTML date-picker *keyboard* interaction is not exercised — date and
datetime-local fields are set by assigning their ISO value via JavaScript
and dispatching the events the page's own validation depends on, then
re-reading the value to confirm the browser accepted it; actual submission
still goes through the real UI button. No continuous integration workflow
exists yet for `job-search-hub-tests`; this remains an outstanding Phase 1
item for this repository, not something this milestone introduces or claims
as complete.

## 6. Chronology: Transcript End and Subsequent Events

This section separates what the transcript itself records from what is
known, from other sources, to have happened afterward. The transcript was
not altered to insert any of the later events below; only this document and
[`docs/test-journal.md`](../test-journal.md) record them.

### At the end of the transcript

The transcript ends with Claude reporting the three corrections from
Section 4 back to the human for review. Codex's review of those
corrections, and human approval, are **not recorded in the transcript
itself** - it ends with Claude's correction report, not with a second
Codex verification pass.

### Subsequently, outside the transcript

The following did not happen within, and is not described by, this Claude
Code transcript. It is recorded here on the basis of a Codex review context
supplied directly for this documentation task, together with Git evidence
checked locally - not inferred or reconstructed from the transcript:

- In a separate Codex conversation, Codex reviewed Claude's corrections and
  confirmed all three findings from Section 2 resolved.
- The human then performed the milestone commit directly, through VS Code
  (not through Claude).

### Git evidence

`job-search-hub-tests` `main` is at commit `275c700` ("Add isolated
Selenium workflow tests with SQL verification"), verified locally via
`git log`/`git show` at the time this document was written. Its diff
contains both Claude's original implementation and Claude's corrections to
Codex's three findings together, in a single commit - consistent with the
corrections being made and confirmed resolved before the human's single
commit action, rather than committed separately.

### This documentation pass

The transcript-sanitization and highlights work this document and
[`docs/test-journal.md`](../test-journal.md) describe was prepared after commit `275c700` and
remains **uncommitted**, pending Codex's review and human approval -
including the redaction and chronology corrections recorded in this
revision.
