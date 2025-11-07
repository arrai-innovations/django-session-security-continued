import datetime
import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


pytestmark = [pytest.mark.django_db, pytest.mark.selenium]


def _press_space(driver):
    driver.find_element(By.TAG_NAME, "body").send_keys(Keys.SPACE)


def _iterate_windows(driver):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        yield


def test_warning_shows_and_session_expires(selenium_browser, activity_window):
    start = datetime.datetime.now()

    for _ in _iterate_windows(selenium_browser):
        warning = WebDriverWait(selenium_browser, activity_window.max_warn_after).until(
            expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
        )
        assert warning.is_displayed()

    delta = datetime.datetime.now() - start
    assert delta.seconds >= activity_window.min_warn_after
    assert delta.seconds <= activity_window.max_warn_after

    for _ in _iterate_windows(selenium_browser):
        password_field = WebDriverWait(selenium_browser, activity_window.max_expire_after).until(
            expected_conditions.visibility_of_element_located((By.ID, "id_password"))
        )
        assert password_field.is_displayed()
        delta = datetime.datetime.now() - start
        assert delta.seconds >= activity_window.min_expire_after
        assert delta.seconds <= activity_window.max_expire_after


def test_activity_hides_warning(selenium_browser, activity_window):
    time.sleep(activity_window.min_warn_after * 0.7)
    WebDriverWait(selenium_browser, activity_window.max_warn_after).until(
        expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
    )

    _press_space(selenium_browser)

    for _ in _iterate_windows(selenium_browser):
        pass

    assert WebDriverWait(selenium_browser, 20).until(
        expected_conditions.invisibility_of_element_located((By.ID, "session_security_warning"))
    )


def test_activity_prevents_warning(selenium_browser, activity_window):
    time.sleep(activity_window.min_warn_after * 0.7)
    _press_space(selenium_browser)
    start = datetime.datetime.now()

    warning = WebDriverWait(selenium_browser, activity_window.max_warn_after).until(
        expected_conditions.visibility_of_element_located((By.ID, "session_security_warning"))
    )
    assert warning.is_displayed()

    for _ in _iterate_windows(selenium_browser):
        pass

    delta = datetime.datetime.now() - start
    assert delta.seconds >= activity_window.min_warn_after
