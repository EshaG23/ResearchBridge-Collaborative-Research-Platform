from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from apps.core.views import dashboard

urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:login", permanent=False)),
    path("accounts/", include("apps.accounts.urls")),
    path("dashboard/", dashboard, name="dashboard"),
    path("profile/", include("apps.profiles.urls")),
    path("mentorship/", include("apps.mentorship.urls")),
    path("applications/", include("apps.recruitment.urls")),
    path("projects/", include("apps.projects.urls")),
    path("documents/", include("apps.documents.urls")),
    path("notifications/", include("apps.notifications.urls")),
    path("admin/", admin.site.urls),
]

from django.conf import settings
from apps.core.views import ui_preview

if settings.DEBUG:
    urlpatterns += [
        path("dev/ui/", ui_preview, name="ui-preview"),
        path("dev/ui/<str:section>/", ui_preview, name="ui-preview-section"),
    ]
