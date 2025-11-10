import time

from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include
from django.urls import path
from django.views import generic


class SleepView(generic.TemplateView):
    def get(self, request, *args, **kwargs):
        time.sleep(int(request.GET.get("seconds", 0)))
        return super().get(request, *args, **kwargs)


urlpatterns = [
    path("", generic.TemplateView.as_view(template_name="home.html")),
    path("sleep/", login_required(SleepView.as_view(template_name="home.html")), name="sleep"),
    path("admin/", admin.site.urls),
    path("auth/", include("django.contrib.auth.urls")),
    path("session_security/", include("session_security.urls")),
    path("ignore/", login_required(generic.TemplateView.as_view(template_name="home.html")), name="ignore"),
    path(
        "passive/",
        login_required(generic.TemplateView.as_view(template_name="home.html")),
        name="passive",
    ),
    path(
        "template/",
        login_required(generic.TemplateView.as_view(template_name="template.html")),
        name="template",
    ),
]
