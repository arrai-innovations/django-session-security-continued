import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
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


TIMEOUT_PADDING_ENV = "SESSION_SECURITY_TIMEOUT_PADDING"


def _timeout_padding_seconds() -> float:
    raw_value = os.environ.get(TIMEOUT_PADDING_ENV)
    if not raw_value:
        return 0.0
    try:
        padding = float(raw_value)
    except ValueError as exc:
        raise RuntimeError(
            f"{TIMEOUT_PADDING_ENV} must be a number representing seconds of extra wait time; got {raw_value!r}."
        ) from exc
    return max(0.0, padding)


@pytest.fixture
def activity_window(settings):
    expire_after = settings.SESSION_SECURITY_EXPIRE_AFTER
    warn_after = settings.SESSION_SECURITY_WARN_AFTER
    padding = _timeout_padding_seconds()
    warn_margin = 0.5  # always keep at least this much headroom before expiry
    max_warn_cap = max(warn_after, expire_after - warn_margin)
    max_warn_after = min(expire_after * 0.9 + padding, max_warn_cap)
    return ActivityWindow(
        min_warn_after=warn_after,
        max_warn_after=max_warn_after,
        min_expire_after=expire_after,
        max_expire_after=expire_after * 1.5 + padding,
    )


@pytest.fixture
def frozen_time(monkeypatch):
    class FrozenDateTime:
        def __init__(self):
            self._current = datetime.now()

        def now(self):
            return self._current

        def advance(self, seconds: float):
            self._current += timedelta(seconds=seconds)

    freezer = FrozenDateTime()
    monkeypatch.setattr("session_security.middleware.datetime", freezer)
    monkeypatch.setattr("session_security.views.datetime", freezer)
    return freezer


JS_COVERAGE_ENV = "SESSION_SECURITY_JS_COVERAGE"
JS_COVERAGE_STATIC_PATH = "session_security/coverage/script.js"
REPO_ROOT = Path(__file__).resolve().parents[2]
NYC_DIR = Path(".nyc_output")


@pytest.fixture
def selenium_browser(live_server, admin_user, settings):
    use_js_coverage = bool(os.environ.get(JS_COVERAGE_ENV))
    if use_js_coverage:
        settings.SESSION_SECURITY_JS_PATH = JS_COVERAGE_STATIC_PATH
        coverage_bundle = REPO_ROOT / "session_security" / "static" / "session_security" / "coverage" / "script.js"
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
                "Instrumented session security script was not loaded; check SESSION_SECURITY_JS_PATH configuration."
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
