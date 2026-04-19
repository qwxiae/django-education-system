from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import Category, Course, Enrollment, Module


class ModuleInline(admin.TabularInline):
    """
    Modules exist in relation to Courses.
    No point in making modules outside a Course.
    """

    model = Module
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Categories are seeded. Teachers choose from given Category."""

    search_fields = ["name"]
    # Dont add description TextField looks bad in admin
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ["name"]}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    search_fields = ["title", "author__email"]
    list_filter = ["is_published", "category"]
    inlines = [ModuleInline]

    readonly_fields = ["created_at", "updated_at"]
    prepopulated_fields = {"slug": ["title"]}
    list_display = [
        "author",
        "category",
        "title",
        "slug",
        "is_published",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        (None, {"fields": ("author", "category", "title", "slug", "is_published")}),
        ("Content", {"fields": ("description", "promo_content", "cover")}),
        ("Dates", {"fields": ("created_at", "updated_at")}),
    )
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    search_fields = ["user__email", "course__title"]
    readonly_fields = ["enrolled_at", "last_active_at"]
    list_display = ["user", "course", "enrolled_at", "last_active_at"]
