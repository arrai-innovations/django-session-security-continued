"""
SessionSecurityMiddleware is the heart of the security that this application
attemps to provide.

To install this middleware, add to ``settings.MIDDLEWARE``::

    'django_session_security_continued.middleware.SessionSecurityMiddleware'

Place it after authentication middleware.
"""

from datetime import datetime
from datetime import timedelta

import django
from django.urls import Resolver404
from django.urls import resolve
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from django_session_security_continued.utils import get_last_activity
from django_session_security_continued.utils import set_last_activity


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    In charge of maintaining the real 'last activity' time, and log out the
    user if appropriate.
    """

    def is_passive_request(self, request):
        """Should we skip activity update on this URL/View."""
        from django_session_security_continued.settings import PASSIVE_URL_NAMES
        from django_session_security_continued.settings import PASSIVE_URLS

        if request.path in PASSIVE_URLS:
            return True

        try:
            match = resolve(request.path)
            # TODO: check namespaces too
            if match.url_name in PASSIVE_URL_NAMES:
                return True
        except Resolver404:
            pass

        return False

    def get_expire_seconds(self, request):
        """Return time (in seconds) before the user should be logged out."""
        from django_session_security_continued.settings import EXPIRE_AFTER

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
        # This is a separate method to allow for subclasses to override the
        # behavior, mostly.
        if django.VERSION < (1, 10):
            is_authenticated = request.user.is_authenticated()
        else:
            is_authenticated = request.user.is_authenticated

        return is_authenticated

    def do_logout(self, request):
        # This is a separate method to allow for subclasses to override the
        # behavior, mostly.
        from django.contrib.auth import logout

        logout(request)
