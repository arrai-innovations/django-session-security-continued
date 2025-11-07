import pytest


pytestmark = pytest.mark.django_db


def test_default_template_has_no_return_to_url(client, user):
    client.force_login(user)
    response = client.get("/template/")
    assert b"returnToUrl" not in response.content


def test_setting_enables_return_to_url(client, user, settings):
    client.force_login(user)
    settings.SESSION_SECURITY_REDIRECT_TO_LOGOUT = True
    response = client.get("/template/")
    assert b"returnToUrl" in response.content
