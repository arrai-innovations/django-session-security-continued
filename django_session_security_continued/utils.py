"""Helpers to support json encoding of session data"""

from datetime import datetime


def set_last_activity(session, dt):
    """Set the last activity datetime as a string in the session."""
    session["_session_security"] = dt.strftime("%Y-%m-%dT%H:%M:%S.%f")


def get_last_activity(session):
    """Return the stored last-activity timestamp as a datetime."""
    value = session["_session_security"]
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
