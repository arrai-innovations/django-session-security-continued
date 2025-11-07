from dataclasses import dataclass

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


@pytest.fixture
def selenium_browser(live_server, admin_user):
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

    yield driver

    driver.quit()
