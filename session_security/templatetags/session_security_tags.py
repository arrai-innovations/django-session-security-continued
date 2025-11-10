from django import template
from django.conf import settings

from session_security.settings import EXPIRE_AFTER
from session_security.settings import WARN_AFTER


register = template.Library()


@register.filter
def expire_after(request):
    return EXPIRE_AFTER


@register.filter
def warn_after(request):
    return WARN_AFTER


@register.filter
def redirect_to_logout(request):
    redirect = getattr(settings, "SESSION_SECURITY_REDIRECT_TO_LOGOUT", False)
    return redirect


@register.simple_tag
def session_security_script_path():
    return getattr(settings, "SESSION_SECURITY_JS_PATH", "session_security/script.js")
