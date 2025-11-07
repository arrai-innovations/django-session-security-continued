# django-session-security-continued

[![code style: ruff][]][ruff] [![code style: prettier][]][prettier] ![pytest status][] ![coverage status][] ![ruff status][] ![pip-audit status][]

<!--prettier-ignore-start-->
<!--TOC-->

- [About](#about)
- [Requirements / Compatibility](#requirements--compatibility)
- [Installation](#installation)
- [Single Sign-On (SSO) Considerations](#single-sign-on-sso-considerations)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)

<!--TOC-->
<!--prettier-ignore-end-->

## About

A minimal JavaScript and Django middleware app that automatically logs out users after inactivity. It tracks activity across all browser tabs, warns users before logging them out, and protects sensitive data.

Built for CRMs, intranets, and similar applications, it prevents abandoned sessions from staying open when users leave their workstations. Unlike simply setting session expiry, this approach ensures users aren’t logged out while reading, reviewing data, or filling out forms; preserving their work and reducing frustration while still enforcing inactivity-based security.

This fork is maintained by Arrai Innovations Inc. based on the original [`django-session-security`](https://github.com/yourlabs/django-session-security) by Yourlabs.

## Requirements / Compatibility

- **Django:** 4.2, 5.2
    - `django.contrib.staticfiles`
- **Python:** 3.9, 3.10, 3.11, 3.12

## Installation

```console
# Install the package
$ pip install django-session-security-continued
```

```python
# settings.py

INSTALLED_APPS = [
    # Add the app
    'django_session_security_continued',
    # ...
]

MIDDLEWARE = [
    # Make sure this comes AFTER the authentication middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_session_security_continued.middleware.SessionSecurityMiddleware',
    # ...
]

TEMPLATES = [
    {
        # ...
        'OPTIONS': {
            'context_processors': [
                # Ensure this is present
                'django.template.context_processors.request',
                # ...
            ],
        },
    },
]

# Optional settings (see configuration section for details)
SESSION_SECURITY_WARN_AFTER = 540          # Warn user after 9 minutes
SESSION_SECURITY_EXPIRE_AFTER = 600        # Log out after 10 minutes
SESSION_SECURITY_PASSIVE_URLS = []         # URLs that won’t reset the timer
SESSION_SECURITY_REDIRECT_TO_LOGOUT = False  # Set True for SSO setups
SESSION_SECURITY_PING_URL = '/session_security/ping/'  # Activity endpoint
```

```python
# urls.py

from django.urls import include, path

urlpatterns = [
    # Add this route to enable the session security endpoints
    path('session_security/', include('django_session_security_continued.urls')),
    # ...
]
```

```html
<!-- base.html (or equivalent) -->
{% load static %}
...
{% include "session_security/all.html" %}
<script>
    // optional: disable form discard confirmation dialog
    sessionSecurity.confirmFormDiscard = undefined;
    // optional: register custom activity
    sessionSecurity.activity();
</script>
```

## Single Sign-On (SSO) Considerations

When using SSO, the default page reload after timeout may cause automatic re-login if the SSO session remains valid. Set `SESSION_SECURITY_REDIRECT_TO_LOGOUT = True` to explicitly end the app session by redirecting to `LOGOUT_REDIRECT_URL`. Note that this does **not** terminate the SSO provider session; configure a matching timeout on your SSO server for full coverage.

## Development

This project uses `uv` for managing the development environment. To set up the development environment, follow these steps:

```console
# Clone the repository
$ git clone https://github.com/arrai-innovations/django-session-security-continued.git
$ cd django-session-security-continued

# Ensure a compatible Python (>=3.9) is installed

# Install uv if not already installed
$ pip install --user --upgrade uv

# Create and sync the dev environment
#  (default group includes dev dependencies)
$ uv sync

# (Optional) Run Git hooks setup
$ uv run pre-commit install
```

## Testing

Chrome is required for the Selenium end-to-end tests (Selenium Manager will download the matching chromedriver automatically). Run the full suite with pytest:

```console
$ uv run pytest
```

If Chrome isn’t available (or you only want the fast unit tests), skip the browser suite with `uv run pytest -k "not test_script"` until we add explicit markers.

## Contributing

Contributions are welcome. Please fork the repository and create a pull request with your changes. We reserve the right to review and modify your contributions before merging them into the main branch. By submitting a change you confirm that:

- You wrote the code (or have the right to contribute it), and
- You’re happy for it to be released under this project’s MIT license.

[code style: ruff]: https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge
[ruff]: https://docs.astral.sh/ruff/formatter/#style-guide
[code style: prettier]: https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=for-the-badge
[prettier]: https://github.com/prettier/prettier
[pytest status]: https://docs.arrai.dev/django-session-security-continued/artifacts/main/pytest.svg
[coverage status]: https://docs.arrai.dev/django-session-security-continued/artifacts/main/pytest.coverage.svg
[ruff status]: https://docs.arrai.dev/django-session-security-continued/artifacts/main/ruff.svg
[pipenv]: https://github.com/pypa/pipenv
[pip-audit status]: https://docs.arrai.dev/django-session-security-continued/artifacts/main/pip-audit.svg
