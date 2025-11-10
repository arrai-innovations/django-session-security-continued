from datetime import datetime
from datetime import timedelta

import pytest
from django.test import override_settings

from session_security.utils import get_last_activity
from session_security.utils import set_last_activity


pytestmark = pytest.mark.django_db


def test_auto_logout(authenticated_client, activity_window, frozen_time):
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session
    frozen_time.advance(activity_window.max_expire_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" not in authenticated_client.session


def test_last_activity_in_future(authenticated_client, activity_window):
    now = datetime.now()
    future = now + timedelta(seconds=activity_window.max_expire_after * 2)
    set_last_activity(authenticated_client.session, future)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_non_javascript_browse_no_logout(authenticated_client, activity_window, frozen_time):
    authenticated_client.get("/admin/")
    frozen_time.advance(activity_window.max_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session
    frozen_time.advance(activity_window.min_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_javascript_activity_no_logout(authenticated_client, activity_window, frozen_time):
    authenticated_client.get("/admin/")
    frozen_time.advance(activity_window.max_warn_after)
    authenticated_client.get("/session_security/ping/?idleFor=1")
    assert "_auth_user_id" in authenticated_client.session
    frozen_time.advance(activity_window.min_warn_after)
    authenticated_client.get("/admin/")
    assert "_auth_user_id" in authenticated_client.session


def test_url_names(authenticated_client, activity_window, frozen_time):
    authenticated_client.get("/admin/")
    activity1 = get_last_activity(authenticated_client.session)
    frozen_time.advance(min(2, activity_window.min_warn_after))
    authenticated_client.get("/admin/")
    activity2 = get_last_activity(authenticated_client.session)
    assert activity2 > activity1
    frozen_time.advance(min(2, activity_window.min_warn_after))
    authenticated_client.get("/ignore/")
    activity3 = get_last_activity(authenticated_client.session)
    assert activity2 == activity3


@override_settings(SESSION_SECURITY_PASSIVE_URLS=["/passive/"])
def test_passive_urls(authenticated_client, activity_window, frozen_time):
    authenticated_client.get("/admin/")
    activity1 = get_last_activity(authenticated_client.session)
    frozen_time.advance(min(2, activity_window.min_warn_after))
    authenticated_client.get("/passive/")
    activity2 = get_last_activity(authenticated_client.session)
    assert activity1 == activity2


def test_idle_for_non_integer(authenticated_client):
    authenticated_client.get("/admin/")
    activity1 = get_last_activity(authenticated_client.session)
    authenticated_client.get("/session_security/ping/?idleFor=not-a-number")
    activity2 = get_last_activity(authenticated_client.session)
    assert activity1 == activity2


def test_idle_for_negative(authenticated_client):
    authenticated_client.get("/admin/")
    activity1 = get_last_activity(authenticated_client.session)
    authenticated_client.get("/session_security/ping/?idleFor=-5")
    activity2 = get_last_activity(authenticated_client.session)
    # Negative values are coerced to zero, so activity should stay unchanged.
    assert activity1 == activity2
