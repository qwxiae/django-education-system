from django.core.cache import cache
from django.db.models import Count
from apps.core.cache_keys import CacheKeys
from apps.core.cache_timeouts import CacheTimeouts
from .models import Course, Category, Enrollment

def get_categories():
    return cache.get_or_set(
        CacheKeys.CATEGORIES, 
        lambda: list(Category.objects.all()),
        timeout=CacheTimeouts.Category.LIST
    )

def get_featured_courses():
    return cache.get_or_set(
        CacheKeys.FEATURED_COURSES,
        lambda: list(
            Course.objects
            .filter(is_published=True)
            .select_related("category", "author")
            .order_by("-created_at")[:6]
        ),
        timeout=CacheTimeouts.Course.FEATURED
    )

def get_course_detail(slug):
    return cache.get_or_set(
        CacheKeys.course(slug),
        lambda: Course.objects
            .select_related("author", "category")
            .prefetch_related("modules")
            .annotate(module_count=Count("modules"))
            .filter(slug=slug, is_published=True)
            .first(),
        timeout=CacheTimeouts.Course.DETAIL
    )

def get_published_courses(category_slug=None, q=None):
    return cache.get_or_set(
        CacheKeys.catalog(category_slug or "", q or "",),
        lambda: list(
            Course.objects
            .select_related("category", "author")
            .filter(is_published=True)
            .filter(**{"category__slug": category_slug} if category_slug else {})
            .filter(**{"title__icontains": q} if q else {})
        ),
        timeout=CacheTimeouts.Course.LIST
    )


def invalidate_course_cache(slug=None):
    cache.delete(CacheKeys.course(slug))
    cache.delete(CacheKeys.FEATURED_COURSES)
    