import time
from datetime import datetime
from datetime import timedelta

import pytest

from django_session_security_continued.utils import get_last_activity
from django_session_security_continued.utils import set_last_activity


pytestmark = pytest.mark.django_db


def test_auto_logout(authenticated_client, activity_window):
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session
    time.sleep(activity_window.max_expire_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" not in authenticated_client.session


def test_last_activity_in_future(authenticated_client, activity_window):
    now = datetime.now()
    future = now + timedelta(seconds=activity_window.max_expire_after * 2)
    set_last_activity(authenticated_client.session, future)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_non_javascript_browse_no_logout(authenticated_client, activity_window):
    authenticated_client.get("/admin/")
    time.sleep(activity_window.max_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session
    time.sleep(activity_window.min_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_javascript_activity_no_logout(authenticated_client, activity_window):
    authenticated_client.get("/admin/")
    time.sleep(activity_window.max_warn_after)
    authenticated_client.get("/session_security/ping/?idleFor=1")
    assert "_auth_user_id" in authenticated_client.session
    time.sleep(activity_window.min_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_url_names(authenticated_client, activity_window):
    authenticated_client.get("/admin/")
    activity1 = get_last_activity(authenticated_client.session)
    time.sleep(min(2, activity_window.min_warn_after))
    authenticated_client.get("/admin/")
    activity2 = get_last_activity(authenticated_client.session)
    assert activity2 > activity1
    time.sleep(min(2, activity_window.min_warn_after))
    authenticated_client.get("/ignore/")
    activity3 = get_last_activity(authenticated_client.session)
    assert activity2 == activity3
