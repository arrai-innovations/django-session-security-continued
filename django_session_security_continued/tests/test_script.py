import datetime
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from django_session_security_continued.tests.test_base import BaseLiveServerTestCase


class ScriptTestCase(BaseLiveServerTestCase):
    def test_warning_shows_and_session_expires(self):
        start = datetime.datetime.now()

        for win in self.sel.window_handles:
            self.sel.switch_to.window(win)
            el = WebDriverWait(self.sel, self.max_warn_after).until(
                expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
            )
            assert el.is_displayed()
        end = datetime.datetime.now()
        delta = end - start

        self.assertGreaterEqual(delta.seconds, self.min_warn_after)
        self.assertLessEqual(delta.seconds, self.max_warn_after)

        for win in self.sel.window_handles:
            self.sel.switch_to.window(win)
            el = WebDriverWait(self.sel, self.max_expire_after).until(
                expected_conditions.visibility_of_element_located((By.ID, "id_password"))
            )
            assert el.is_displayed()
            delta = datetime.datetime.now() - start
            self.assertGreaterEqual(delta.seconds, self.min_expire_after)
            self.assertLessEqual(delta.seconds, self.max_expire_after)

    def test_activity_hides_warning(self):
        time.sleep(6 * 0.7)
        WebDriverWait(self.sel, self.max_warn_after).until(
            expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
        )

        self.press_space()

        for win in self.sel.window_handles:
            self.sel.switch_to.window(win)

        el = WebDriverWait(self.sel, 20).until(
            expected_conditions.invisibility_of_element_located((By.ID, "session_security_warning"))
        )

        assert not el.is_displayed()

    def test_activity_prevents_warning(self):
        time.sleep(self.min_warn_after * 0.7)
        self.press_space()
        start = datetime.datetime.now()
        el = WebDriverWait(self.sel, self.max_warn_after).until(
            expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
        )
        assert el.is_displayed()

        for win in self.sel.window_handles:
            self.sel.switch_to.window(win)

        delta = datetime.datetime.now() - start
        self.assertGreaterEqual(delta.seconds, self.min_warn_after)
