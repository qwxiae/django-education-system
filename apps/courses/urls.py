from django.urls import path
from . import views

app_name = "courses"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    
    # === Catalog ===
    # search and list all courses
    path("catalog/", views.catalog_view, name="catalog"),
    # list all categories
    path("catalog/categories/", views.categories_view, name="categories"),
    path("catalog/categories/<slug:slug>/", views.category_view, name="category_courses"),


    # === Courses ====
    path("courses/<slug:slug>/", views.course_detail_view, name="course_detail"),
    
    path("courses/<slug:slug>/enroll/", views.enroll_view, name="enroll"),
    path("courses/<slug:slug>/unenroll/", views.unenroll_view, name="unenroll"),

    # show authenticated users enrolled courses
    path("learn/", views.my_courses_view, name="my_courses"),

]