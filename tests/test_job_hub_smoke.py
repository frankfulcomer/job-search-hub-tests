def test_job_hub_home_page_loads(driver):
    driver.get("http://127.0.0.1:5000")

    assert driver.title == "Job Hub - Home"
    assert "Welcome to Job Hub" in driver.page_source