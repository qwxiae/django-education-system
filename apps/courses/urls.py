from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    
    # === Catalog ===
    # search and list all courses
    path("catalog/", views.catalog_view, name="catalog"),
    
    # === Courses ====
    path("courses/<slug:slug>/", views.course_detail_view, name="course_detail"),
    
    path("courses/<slug:slug>/enroll/", views.enroll_view, name="enroll"),
    path("courses/<slug:slug>/unenroll/", views.unenroll_view, name="unenroll"),

    # show authenticated users enrolled courses
    path("learn/", views.my_courses_view, name="my_courses"),

    # === Lessons ===
    # path(
    #   "courses/<slug:slug>/modules/<module_id:str>/lessons/",
    #   views.module_lessons_view,
    #   name="module_lessons"
    # )
    # path(
    #   "courses/<slug:slug>/modules/<module_id:str>/lessons/<lesson_id:str>/",
    #   views.lesson_detail_view,
    #   name="lesson"
    # )
]
