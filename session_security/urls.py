"""
One url meant to be used by JavaScript.

session_security_ping
    Connects the PingView.

To install this url, include it in ``urlpatterns`` definition in ``urls.py``,
ie::

    urlpatterns = [
        # ....
        path("session_security/", include("session_security.urls")),
        # ....
    ]

"""

from django.urls import re_path

from session_security.views import PingView


urlpatterns = [
    re_path(
        "ping/$",
        PingView.as_view(),
        name="session_security_ping",
    )
]
