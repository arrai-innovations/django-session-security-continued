"""
SessionSecurityMiddleware is the heart of the security that this application
attemps to provide.

To install this middleware, add to ``settings.MIDDLEWARE``::

    'session_security.middleware.SessionSecurityMiddleware'

Place it after authentication middleware.
"""

from datetime import datetime
from datetime import timedelta

from django.conf import settings as django_settings
from django.urls import Resolver404
from django.urls import resolve
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from session_security.utils import get_last_activity
from session_security.utils import set_last_activity


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    In charge of maintaining the real 'last activity' time, and log out the
    user if appropriate.
    """

    def is_passive_request(self, request):
        """Should we skip activity update on this URL/View."""
        from session_security.settings import PASSIVE_URL_NAMES as DEFAULT_PASSIVE_URL_NAMES
        from session_security.settings import PASSIVE_URLS as DEFAULT_PASSIVE_URLS

        passive_urls = getattr(
            django_settings,
            "SESSION_SECURITY_PASSIVE_URLS",
            DEFAULT_PASSIVE_URLS,
        )
        passive_url_names = getattr(
            django_settings,
            "SESSION_SECURITY_PASSIVE_URL_NAMES",
            DEFAULT_PASSIVE_URL_NAMES,
        )

        if request.path in passive_urls:
            return True

        try:
            match = resolve(request.path)
            # TODO: check namespaces too
            if match.url_name in passive_url_names:
                return True
        except Resolver404:
            pass

        return False

    def get_expire_seconds(self, request):
        """Return time (in seconds) before the user should be logged out."""
        from session_security.settings import EXPIRE_AFTER

        return EXPIRE_AFTER

    def process_request(self, request):
        """Update last activity time or logout."""
        if not self.is_authenticated(request):
            return

        now = datetime.now()
        if "_session_security" not in request.session:
            set_last_activity(request.session, now)
            return

        delta = now - get_last_activity(request.session)
        expire_seconds = self.get_expire_seconds(request)
        if delta >= timedelta(seconds=expire_seconds):
            self.do_logout(request)
        elif request.path == reverse("session_security_ping") and "idleFor" in request.GET:
            self.update_last_activity(request, now)
        elif not self.is_passive_request(request):
            set_last_activity(request.session, now)

    def update_last_activity(self, request, now):
        """
        If ``request.GET['idleFor']`` is set, check if it refers to a more
        recent activity than ``request.session['_session_security']`` and
        update it in this case.
        """
        last_activity = get_last_activity(request.session)
        server_idle_for = (now - last_activity).seconds

        # Gracefully ignore non-integer values
        try:
            client_idle_for = int(request.GET["idleFor"])
        except ValueError:
            return

        # Disallow negative values, causes problems with delta calculation
        if client_idle_for < 0:
            client_idle_for = 0

        if client_idle_for < server_idle_for:
            # Client has more recent activity than we have in the session
            last_activity = now - timedelta(seconds=client_idle_for)

        # Update the session
        set_last_activity(request.session, last_activity)

    def is_authenticated(self, request):
        """Provide a hook for subclasses that want custom auth logic."""
        return request.user.is_authenticated

    def do_logout(self, request):
        """Provide a hook for subclasses that want a custom logout implementation."""
        from django.contrib.auth import logout

        logout(request)
