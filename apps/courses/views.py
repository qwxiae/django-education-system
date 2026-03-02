from django.shortcuts import render

def home_view(request):
    return render(request, "courses/home.html")

def about_view(request):
    return render(request, "courses/about.html")

def catalog_view(request):
    return render(request, "courses/home.html")

def categories_view(request):
    return render(request, "courses/home.html")

def category_view(request, category_id: int):
    return render(request, "courses/home.html")

def course_detail_view(request, course_id: int):
    return render(request, "courses/home.html")

# Only for authenticated users
def enroll_view(request, course_id: int):
    return render(request, "courses/home.html")

# Only for authenticated users
def unenroll_view(request, course_id: int):
    return render(request, "courses/home.html")

# Only for authenticated users
def my_courses_view(request):
    return render(request, "courses/home.html")

