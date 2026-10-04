import os
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# This repository treats Job Search Hub as an externally observed system
# under test (docs/test-strategy.md): these fixtures start and stop a real
# application process and own a fresh, isolated SQLite file per test. They
# never read, modify, or point at the user's personal application database.

TESTS_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APP_DIR = TESTS_REPO_ROOT.parent / "job-search-hub"

STARTUP_TIMEOUT_SECONDS = 15
POLL_INTERVAL_SECONDS = 0.2
SHUTDOWN_TIMEOUT_SECONDS = 5


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run Chrome with a visible window instead of headless (default: headless).",
    )


@pytest.fixture(scope="session")
def driver(request):
    """One reusable Chrome WebDriver instance for the whole test session.

    Headless by default; pass --headed to watch the browser locally. A
    failure constructing the driver (missing Chrome/driver, display issues,
    etc.) surfaces as a fixture-setup error, distinct from a test assertion
    failure - see README.md "Troubleshooting".
    """
    options = Options()
    if not request.config.getoption("--headed"):
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    browser = webdriver.Chrome(options=options)
    try:
        yield browser
    finally:
        browser.quit()


def _app_dir():
    configured = os.environ.get("JOB_HUB_APP_DIR")
    return Path(configured).resolve() if configured else DEFAULT_APP_DIR.resolve()


def _app_python(app_dir):
    configured = os.environ.get("JOB_HUB_PYTHON")
    if configured:
        return configured
    venv_python = app_dir / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@dataclass
class AppServer:
    base_url: str
    db_path: Path


@pytest.fixture
def app_server(tmp_path):
    """Start a dedicated Job Search Hub process against a fresh, fixture-
    owned SQLite file, and tear it down unconditionally afterward.

    - A fresh temporary database path is used for every test (pytest's
      tmp_path), so ordinary application startup can initialize schema and
      seed reference statuses without resetting or touching anything else.
    - A loopback address and a freshly chosen, available port are used, so
      this never attaches to an already-running instance on the normal
      development port.
    - The reloader and debugger are explicitly disabled.
    """
    app_dir = _app_dir()
    if not app_dir.is_dir():
        pytest.fail(
            f"Job Search Hub application directory not found at {app_dir}. "
            "Set JOB_HUB_APP_DIR to the application repository's location "
            "(default assumes a sibling 'job-search-hub' checkout)."
        )

    db_path = tmp_path / "job_hub_test.sqlite3"
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    env = dict(os.environ)
    env["JOB_HUB_DATABASE"] = str(db_path)
    env["FLASK_APP"] = "wsgi.py"
    env.pop("FLASK_DEBUG", None)

    process = subprocess.Popen(
        [
            _app_python(app_dir),
            "-m",
            "flask",
            "run",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--no-debug",
            "--no-reload",
        ],
        cwd=app_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        last_error = None
        ready = False
        while time.monotonic() < deadline:
            if process.poll() is not None:
                pytest.fail(
                    "The Job Search Hub application process exited during "
                    f"startup (exit code {process.returncode}).\n"
                    f"Output:\n{process.stdout.read()}"
                )
            try:
                with urllib.request.urlopen(base_url + "/", timeout=1) as response:
                    ready = response.status == 200
            except (urllib.error.URLError, ConnectionError) as exc:
                last_error = exc
            if ready:
                break
            time.sleep(POLL_INTERVAL_SECONDS)

        if not ready:
            process.kill()
            process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
            pytest.fail(
                f"Timed out waiting {STARTUP_TIMEOUT_SECONDS}s for the "
                f"application to respond at {base_url}/ (last error: "
                f"{last_error})."
            )

        yield AppServer(base_url=base_url, db_path=db_path)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=SHUTDOWN_TIMEOUT_SECONDS)
        if process.stdout:
            process.stdout.close()


@pytest.fixture
def app_db(app_server):
    """A read-only connection to the exact SQLite file this test's
    application process owns.

    This is a persistence oracle, not a way to create test records or call
    business logic (docs/test-strategy.md): tests still create data through
    the UI and use this connection only to confirm what was actually
    written. Opened read-only (URI mode=ro) so a test can never accidentally
    write through this connection, and only ever against the fixture-owned
    path - never a separately supplied or personal database path.
    """
    connection = sqlite3.connect(f"file:{app_server.db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()
