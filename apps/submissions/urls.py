from django.urls import path
from . import views

app_name = "submissions"

urlpatterns = [
    # /courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/attempts:
    # path("attempts/", views.attempts_list, name="attempts_list"),
    # /courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/attempts/{attempt_id}:
    path("attempts/<str:p_id>", views.attempt_detail, name="attempt_detail"),
    path("lessons/<str:lesson_id>/submit/", views.submit_view, name="submit"),
    path("result/<int:submission_id>/", views.result_view, name="result"),
]
