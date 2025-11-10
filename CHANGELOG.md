# Changelog

## Post-fork Releases

### 3.0.0a1 - 2025-11-10

**Breaking changes**
- Dropped support for Django versions earlier than 4.2 and removed the legacy compatibility shims.
- Removed the bundled jQuery dependency; the front-end widget now uses vanilla JS exclusively.

**Developer experience**
- Migrated the entire test suite to pytest with deterministic Selenium helpers and new middleware coverage.
- Added Ruff, ESLint, Prettier, and pre-commit hooks (including commitlint) to standardize formatting and linting across Python and JS code.
- Instrumented the JavaScript bundle via Vite + Istanbul, added coverage reporting scripts, and documented how to run them.

**CI/CD**
- Replaced the old GitHub Actions workflow with a CircleCI pipeline that tests Python 3.9–3.12, publishes coverage artifacts, and now builds/publishes packages via dedicated jobs.
- Refreshed the README with status badges and updated contributor/development guidance.

---

## Pre-fork Releases

### 2.6.7
- Release.

### 2.6.7rc1
- Moved CI from Travis CI to GitHub Actions.
- Added Django 4.0 support.

### 2.6.6
- Added Django 3.0 support.
- Fixed tests (thanks @jsm222).

### 2.6.1
- #113: Check if session expired on activity (thanks @rbntimes).

### 2.6.0
- Release.

### 2.6.0rc1
- #103: Django 2.0 `urlresolvers` import fix (thanks @Ruffle0).
- #98: Call `is_authenticated` property instead of function for Django 2.0 (thanks @tpeaton).
- #105: Ensure `setTimeout()` millisecond parameter does not exceed max value (thanks @abottc).
- Updated Polish translation (thanks @mpasternak).

### 2.5.1
- #90: Added `SESSION_SECURITY_PASSIVE_URL_NAMES` setting.

### 2.5.0
- #79: Removed compiled binary from source to comply with Debian policy (thanks @nirgal).
- #81: Added Django 1.10 support (thanks @eriktelepovsky).
- #84: Added a11y support to modal dialog (thanks @lynnco).
- #85: Added mobile device activity support (thanks @kalekseev).
- #88: Updated Dutch translation (thanks @rdekker1).
- #91: Test Django 1.11 and 2.0 instead of 1.7 (thanks @jpic).

### 2.4.0
- #75: Fixed vulnerability when `SESSION_EXPIRE_AT_BROWSER_CLOSE` is off.
- #77: Fixed crash when `SESSION_EXPIRE_AT_BROWSER_CLOSE` is off.
- #78: Updated test matrix to include Django 1.10 + master.
- #74: Created security mailing list.

Thanks @ClaytonDelay for reporting the issue. If you cannot set
`SESSION_EXPIRE_AT_BROWSER_CLOSE = True`, you must set `SESSION_SECURITY_INSECURE = True`
to start the project (not recommended).

### 2.3.3
- #69: Encode response to JSON (thanks @Tatsh).

### 2.3.2
- #58: Allow custom expiration based on request (#65) (thanks @mjschultz).

### 2.3.1
- #57: Added `redirectTo` parameter to the script (thanks Andrei Coman).
- Stabilized tests with `django-sbo-selenium`.
- Added Django 1.10 support.

### 2.3.0
- Deprecated support for Django < 1.6.

### 2.2.5
- #56: Added Django 1.9 support (thanks @eriktelepovsky).

### 2.2.4
- #43: Throttled `lastActivity` updates to once per second (thanks @cuu508).

### 2.2.3
- #31: Removed a stray `.mo` file.

### 2.2.2
- #21: Added Polish translation.
- #23: Fixed French translation.
- #26: Fixed edge bug discovered in multithreaded environments.
- #30: Used `reverse_lazy` in `settings.py`.
- Added @mschettler, @mattbo, @nirgal, and @mpasternak to AUTHORS.

### 2.2.1
- #24: Centered the modal on the viewport.

### 2.2.0
- Pre-built `.mo` files.

### 2.1.7
- #19: Ensure consistent datetime formatting to prevent random test failures (thanks Scott Sexton).

### 2.1.6
- #18: Added Spanish translation.

### 2.1.5
- #17: Fixed l10n error with long numbers (thanks @jacoor).

### 2.1.4
- #13: Fixed clock sync problems (thanks @krillr).

### 2.1.3
- Added Brazilian Portuguese translation.

### 2.1.2
- Used `{% static %}` instead of `{{ STATIC_URL }}` in `all.html`.

### 2.1.1
- Fixed AUTHORS.
- Added utils to full documentation.
- Promoted project to Production/Stable.

### 2.1.0
- Added Django 1.5 and 1.6 support.
- Fix #6: Added Internet Explorer 8 support.
- Added Python 3.3 support.
- Minor BC break: cannot set datetime objects directly in the session since Django 1.6.
  Use `session_security.utils.get_last_activity()` and `.set_last_activity()` instead of
  touching `session['_session_security']` directly.

### 2.0.6
- Fix #5: Made the list of event types to monitor configurable.

### 2.0.5
- Removed additional debug statements.

### 2.0.4
- Fix #4: Removed debug statement.

### 2.0.3
- Unset `data-dirty` on form submit to prevent `onbeforeunload` prompts.

### 2.0.2
- Added `confirmFormDiscard` and `onbeforeunload` handler.

### 2.0.1
- Switched ping request from POST to GET and removed CSRF code.

### 2.0.0
- Rewrote the project with unit tests.
