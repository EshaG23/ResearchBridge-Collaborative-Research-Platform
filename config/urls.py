from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:login", permanent=False)),
    path("accounts/", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
]
