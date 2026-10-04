"""Manual, optional utility for ad-hoc exploration of Job Search Hub against
a dedicated throwaway database - NOT used by the automated pytest suite.

The automated tests (tests/conftest.py) now own their own database
lifecycle directly: every test gets a fresh, isolated SQLite file under
pytest's tmp_path, created and schema-initialized by the application's own
normal startup. This script predates that and is kept only for a developer
who wants a standing, resettable database to click around in manually
(e.g. with `flask run`) outside of pytest.

Safety: this script only ever creates or deletes the single, dedicated
file below, under the application's gitignored instance directory - never
the user's personal `job_hub.sqlite3`, and never a path supplied by an
environment variable or command-line argument. Do not point
JOB_HUB_DATABASE at this file while relying on it for anything you want to
keep; running this script deletes and recreates it unconditionally.
"""

from pathlib import Path
import sqlite3


DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "job-search-hub"
    / "src"
    / "instance"
    / "job_hub_selenium.sqlite3"
)

SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "job-search-hub"
    / "src"
    / "job_hub"
    / "schema.sql"
)


if DB_PATH.exists():
    DB_PATH.unlink()

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

with sqlite3.connect(DB_PATH) as connection:
    connection.executescript(SCHEMA_PATH.read_text())
    connection.commit()

print(f"Reset Selenium test database: {DB_PATH}")
