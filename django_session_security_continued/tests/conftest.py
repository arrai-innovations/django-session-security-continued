import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By


@dataclass
class ActivityWindow:
    min_warn_after: float
    max_warn_after: float
    min_expire_after: float
    max_expire_after: float


@pytest.fixture
def admin_user(db, django_user_model):
    return django_user_model.objects.create_superuser(
        username="test",
        email="test@example.com",
        password="test",
    )


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(
        username="regular",
        email="user@example.com",
        password="test",
    )


@pytest.fixture
def authenticated_client(client, admin_user):
    assert client.login(username="test", password="test")
    return client


@pytest.fixture
def activity_window(settings):
    expire_after = settings.SESSION_SECURITY_EXPIRE_AFTER
    warn_after = settings.SESSION_SECURITY_WARN_AFTER
    return ActivityWindow(
        min_warn_after=warn_after,
        max_warn_after=expire_after * 0.9,
        min_expire_after=expire_after,
        max_expire_after=expire_after * 1.5,
    )


JS_COVERAGE_ENV = "SESSION_SECURITY_JS_COVERAGE"
JS_COVERAGE_STATIC_PATH = "session_security/coverage/script.js"
REPO_ROOT = Path(__file__).resolve().parents[2]
NYC_DIR = Path(".nyc_output")


@pytest.fixture
def selenium_browser(live_server, admin_user, settings):
    use_js_coverage = bool(os.environ.get(JS_COVERAGE_ENV))
    if use_js_coverage:
        settings.SESSION_SECURITY_JS_PATH = JS_COVERAGE_STATIC_PATH
        coverage_bundle = (
            REPO_ROOT
            / "django_session_security_continued"
            / "static"
            / "session_security"
            / "coverage"
            / "script.js"
        )
        if not coverage_bundle.exists():
            raise RuntimeError(
                "Instrumented session security bundle not found. "
                "Run `npm install` (once) and `npm run build:coverage` before running Selenium coverage tests."
            )

    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(f"{live_server.url}/admin/")
    driver.find_element(By.NAME, "username").send_keys("test")
    driver.find_element(By.NAME, "password").send_keys("test")
    driver.find_element(By.XPATH, '//input[@value="Log in"]').click()
    driver.execute_script('window.open("/admin/", "other")')

    if use_js_coverage:
        script_sources = driver.execute_script(
            "return Array.from(document.getElementsByTagName('script')).map(s => s.src);"
        )
        if not any("session_security/coverage/script.js" in src for src in script_sources):
            raise RuntimeError(
                "Instrumented session security script was not loaded; "
                "check SESSION_SECURITY_JS_PATH configuration."
            )

    yield driver

    if use_js_coverage:
        NYC_DIR.mkdir(exist_ok=True)
        try:
            coverage_data = driver.execute_script("return window.__coverage__ || null;")
        except Exception:
            coverage_data = None
        if coverage_data:
            filename = f"{uuid.uuid4().hex}.json"
            (NYC_DIR / filename).write_text(json.dumps(coverage_data))

    driver.quit()
