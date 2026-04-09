from django.urls import path
from . import views

app_name = "lessons"

urlpatterns = [
    path("lessons/<str:lesson_id>/", views.lesson_view, name="lesson"),
]
