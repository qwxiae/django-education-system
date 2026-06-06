from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("teach/", views.teach_dashboard_view, name="teach_dashboard"),
    path(
        "teach/courses/<slug:slug>/analytics/",
        views.course_analytics_view,
        name="course_analytics",
    ),
    # course
    path("teach/courses/create/", views.course_create_view, name="course_create"),
    path("teach/courses/<slug:slug>/edit/", views.course_edit_view, name="course_edit"),
    # module
    path(
        "teach/courses/<slug:slug>/modules/create/",
        views.module_create_view,
        name="module_create",
    ),
    path(
        "teach/courses/<slug:slug>/modules/<int:module_id>/edit/",
        views.module_edit_view,
        name="module_edit",
    ),
    # lesson
    path(
        "teach/courses/<slug:slug>/modules/<int:module_id>/lessons/create/",
        views.lesson_create_view,
        name="lesson_create",
    ),
    path(
        "teach/lessons/<str:lesson_id>/edit/",
        views.lesson_edit_view,
        name="lesson_edit",
    ),
    # step
    path(
        "teach/lessons/<str:lesson_id>/steps/create/",
        views.step_create_view,
        name="step_create",
    ),
    path("teach/steps/<int:step_id>/edit/", views.step_edit_view, name="step_edit"),
]
