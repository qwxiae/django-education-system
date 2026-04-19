from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.errors import error_view
from apps.core.views import tinymce_upload

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("tinymce/upload/", tinymce_upload, name="tinymce_upload"),
    path("", include("apps.users.urls")),
    path("", include("apps.courses.urls")),
    path("", include("apps.lessons.urls")),
    path("", include("apps.submissions.urls")),
    path("", include("apps.analytics.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.TESTING and settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
    urlpatterns += debug_toolbar_urls()

if not settings.DEBUG:
    handler404 = lambda request, exception: error_view(request, exception, status=404)
    handler500 = lambda request: error_view(request, status=500)
    handler403 = lambda request, exception: error_view(request, exception, status=403)
    handler400 = lambda request, exception: error_view(request, exception, status=400)