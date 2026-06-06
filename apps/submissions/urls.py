from django.urls import path

from . import views

app_name = "submissions"

urlpatterns = [
    path("lessons/<str:lesson_id>/submit/", views.submit_view, name="submit"),
    path(
        "submissions/<int:submission_id>/result/",
        views.submission_result_view,
        name="result",
    ),
]
