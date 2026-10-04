"""Browser/application smoke: the managed application instance comes up
and serves its home page, using the shared driver and a dedicated,
fixture-owned application process (docs/test-strategy.md)."""

from pages.home_page import HomePage


def test_home_page_loads(driver, app_server):
    home = HomePage(driver, app_server.base_url).load()

    assert home.title == "Job Hub - Home"
    assert home.welcome_heading_text == "Welcome to Job Hub"
