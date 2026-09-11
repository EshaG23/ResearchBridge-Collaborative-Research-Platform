from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

@require_GET
def ui_preview(request, section="discover"):
    # Synthetic presentation only: no project or user records are queried.
    if not settings.DEBUG or section not in {"discover", "projects", "communities", "components"}:
        raise Http404
    labels = {"discover": "Discover projects", "projects": "My projects", "communities": "Communities", "components": "Interface components"}
    return render(request, "core/preview.html", {"section": section, "page_title": labels[section], "ui_preview": True})

