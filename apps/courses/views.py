from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Course, Enrollment
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Prefetch

User = get_user_model()

def home_view(request):
    featured_courses = Course.objects.filter(
        is_published=True
    ).select_related("category", "author").order_by('-created_at')[:6]

    return render(request, "courses/home.html", {
        "featured_courses": featured_courses,
        "categories": Category.objects.all(),
    })

def about_view(request):
    """ Information about the site"""
    return render(request, "courses/about.html")

def catalog_view(request):
    categories = Category.objects.all()
    courses = Course.objects.select_related("category", "author").filter(is_published=True)

    category_slug = request.GET.get("category")
    # search if provided
    q = request.GET.get("q")

    if category_slug:                                         
        courses = courses.filter(category__slug=category_slug)
    if q:
        courses = courses.filter(title__icontains=q)

    return render(request, "courses/catalog.html", {
        "courses": courses,
        "categories": categories,
        "current_category": category_slug,
        "q": q
    })

def course_detail_view(request, slug: str):
    course = get_object_or_404(
        Course.objects
        .select_related("author", "category")
        .annotate(module_count=Count("modules")), 
        slug=slug,
        is_published=True
    )
    
    # modules = (
    #     course.modules
    #     .prefetch_related("lessons")
    #     .annotate(lesson_count=Count("lessons"))
    #     .order_by("order")
    # )

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user,
            course=course
        ).exists()

    return render(request, "courses/course_detail.html", {
        "course": course,
        # "modules": modules,
        "is_enrolled": is_enrolled
    })

@login_required
@require_POST
def enroll_view(request, slug: str):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course)

    if request.headers.get("HX-Request"):
        return render(request, "partials/enroll_button.html", {
            "course": course,
            "is_enrolled": True
        })
    
    return redirect("courses:course_detail", slug=slug)

@login_required
@require_POST
def unenroll_view(request, slug: str):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.filter(user=request.user, course=course).delete()

    if request.headers.get("HX-Request"):
        return render(request, "partials/enroll_button.html", {
            "course": course,
            "is_enrolled": False
        })

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "courses:my_courses"
    return redirect(next_url)

@login_required
def my_courses_view(request):
    enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related("course", "course__category", "course__author")

    return render(request, "courses/my_courses.html", {
        "enrollments": enrollments
    })

