"""Demo-only URL namespaces isolate cookies without changing global settings."""
import re
from django.conf import settings
from django.http import HttpResponseNotFound
from django.urls import get_script_prefix, set_script_prefix

class DemoSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        match = re.match(r'^/demo/([a-f0-9]{32})(/.*)$', request.path_info)
        if not match:
            return self.get_response(request)
        if not settings.DEBUG or settings.AUTHENTICATION_MODE != 'demo':
            return HttpResponseNotFound()
        prefix = '/demo/' + match[1]
        request.demo_session = match[1]
        request.path_info = match[2]
        previous = get_script_prefix()
        set_script_prefix(prefix + '/')
        names = [settings.SESSION_COOKIE_NAME, settings.CSRF_COOKIE_NAME, 'messages']
        for name in names:
            scoped = name + '_' + match[1]
            request.COOKIES.pop(name, None)
            if scoped in request.COOKIES:
                request.COOKIES[name] = request.COOKIES[scoped]
        try:
            response = self.get_response(request)
            for name in names:
                if name in response.cookies:
                    original = response.cookies.pop(name)
                    scoped = name + '_' + match[1]
                    response.cookies[scoped] = original.value
                    for key, value in original.items():
                        if value:
                            response.cookies[scoped][key] = value
                    response.cookies[scoped]['path'] = prefix + '/'
            location = response.get('Location', '')
            if location.startswith('/') and not location.startswith(('//', '/demo/')):
                response['Location'] = prefix + location
            return response
        finally:
            set_script_prefix(previous)
