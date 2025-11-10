import pytest
from django.template.loader import get_template


@pytest.mark.parametrize(
    "template_name",
    [
        "session_security/all.html",
        "session_security/dialog.html",
    ],
)
def test_templates_are_discoverable(template_name):
    """Ensure Django can load templates shipped with the package."""
    template = get_template(template_name)
    assert template is not None
