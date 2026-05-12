from . import services
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.http import Http404

from .models import Category, Course, Enrollment

User = get_user_model()


def home_view(request):
    featured_courses = services.get_featured_courses()

    return render(
        request,
        "courses/home.html",
        {
            "featured_courses": featured_courses,
            "categories": Category.objects.all(),
        },
    )

def catalog_view(request):
    categories = services.get_categories()

    category_slug = request.GET.get("category")
    q = request.GET.get("q")

    courses = services.get_published_courses(category_slug=category_slug, q=q)

    return render(
        request,
        "courses/catalog.html",
        {
            "courses": courses,
            "categories": categories,
            "current_category": category_slug,
            "q": q,
        },
    )


def course_detail_view(request, slug: str):
    course = services.get_course_detail(slug=slug)

    if course is None:
        raise Http404
    modules = (
        course.modules.prefetch_related("lessons")
        .annotate(lesson_count=Count("lessons"))
        .order_by("order")
    )

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(
            user=request.user, course=course
        ).exists()

    return render(
        request,
        "courses/course_detail.html",
        {"course": course, "modules": modules, "is_enrolled": is_enrolled},
    )


@login_required
@require_POST
def enroll_view(request, slug: str):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.get_or_create(user=request.user, course=course)

    if request.headers.get("HX-Request"):
        return render(
            request,
            "partials/enroll_button.html",
            {"course": course, "is_enrolled": True},
        )

    return redirect("courses:course_detail", slug=slug)


@login_required
@require_POST
def unenroll_view(request, slug: str):
    course = get_object_or_404(Course, slug=slug, is_published=True)
    Enrollment.objects.filter(user=request.user, course=course).delete()

    if request.headers.get("HX-Request"):
        return render(
            request,
            "partials/enroll_button.html",
            {"course": course, "is_enrolled": False},
        )

    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or "courses:my_courses"
    )
    return redirect(next_url)


@login_required
def my_courses_view(request):
    enrollments = (
            Enrollment.objects
            .filter(user=request.user)
            .select_related("course", "course__category", "course__author")
        )
    
    return render(request, "courses/my_courses.html", {"enrollments": enrollments})
