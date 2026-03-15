from django.urls import path
from . import views

urlpatterns = [
    # /courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/attempts:
    # path("attempts/", views.attempts_list, name="attempts_list"),
    # /courses/{course_id}/modules/{module_id}/lessons/{lesson_id}/attempts/{attempt_id}:
    path("attempts/<str:p_id>", views.attempt_detail, name="attempt_detail"),
]
