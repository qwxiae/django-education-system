from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("tinymce/upload/", views.tinymce_upload, name="tinymce_upload"),
    path("", include("apps.users.urls")),
    path("", include("apps.courses.urls")),
    path("", include("apps.lessons.urls")),
    path("", include("apps.submissions.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.TESTING and settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns = [
        *urlpatterns,
    ] + debug_toolbar_urls()
