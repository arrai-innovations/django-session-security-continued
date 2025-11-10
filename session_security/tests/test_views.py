from datetime import datetime
from datetime import timedelta

import pytest

from session_security.utils import set_last_activity


pytestmark = pytest.mark.django_db


PING_CASES = (
    (1, 4, "1", True),
    (3, 2, "2", True),
    (5, 5, "5", True),
    (12, 14, '"logout"', False),
)


def test_anonymous_ping(client):
    client.logout()
    client.get("/admin/")
    response = client.get("/session_security/ping/?idleFor=81")
    assert response.content == b'"logout"'


@pytest.mark.parametrize("server_idle, client_idle, expected, authenticated", PING_CASES)
def test_ping(client, admin_user, settings, server_idle, client_idle, expected, authenticated):
    settings.SESSION_SECURITY_WARN_AFTER = 5
    settings.SESSION_SECURITY_EXPIRE_AFTER = 10

    assert client.login(username="test", password="test")
    client.get("/admin/")

    now = datetime.now()
    session = client.session
    set_last_activity(session, now - timedelta(seconds=server_idle))
    session.save()

    response = client.get(f"/session_security/ping/?idleFor={client_idle}")

    assert response.content == expected.encode("utf-8")
    assert ("_auth_user_id" in client.session) is authenticated
