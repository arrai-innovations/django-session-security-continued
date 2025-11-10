import os

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from session_security.settings import EXPIRE_AFTER
from session_security.settings import WARN_AFTER


WAIT_TIME = 5 if not os.environ.get("CI", False) else 30


class SettingsMixin:
    def setUp(self):
        # Give some time for selenium lag
        self.min_warn_after = WARN_AFTER
        self.max_warn_after = EXPIRE_AFTER * 0.9
        self.min_expire_after = EXPIRE_AFTER
        self.max_expire_after = EXPIRE_AFTER * 1.5
        super().setUp()


class BaseLiveServerTestCase(SettingsMixin, StaticLiveServerTestCase, LiveServerTestCase):
    fixtures = ["session_security_test_user"]

    def setUp(self):
        super().setUp()
        options = ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.sel = webdriver.Chrome(options=options)
        self.sel.get(f"{self.live_server_url}/admin/")
        self.sel.find_element(By.NAME, "username").send_keys("test")
        self.sel.find_element(By.NAME, "password").send_keys("test")
        self.sel.find_element(By.XPATH, '//input[@value="Log in"]').click()
        self.sel.execute_script('window.open("/admin/", "other")')

    def press_space(self):
        body = self.sel.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SPACE)

    def tearDown(self):
        self.sel.quit()
        super().tearDown()
