from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:login", permanent=False)),
    path("accounts/", include("apps.accounts.urls")),
    path("admin/", admin.site.urls),
]

from django.conf import settings
from apps.core.views import ui_preview

if settings.DEBUG:
    urlpatterns += [
        path("dev/ui/", ui_preview, name="ui-preview"),
        path("dev/ui/<str:section>/", ui_preview, name="ui-preview-section"),
    ]
