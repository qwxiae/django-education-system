import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    """Categories that group courses"""

    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField(max_length=500, blank=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("courses:category_detail", kwargs={"slug": self.slug})

    class Meta:
        db_table = "courses_category"
        verbose_name_plural = "categories"

    def __str__(self):
        return f"Category(name={self.name})"


class Course(models.Model):
    """Course that stores modules"""

    # Keep the course even if author is gone
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    # Author can assign another one.
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="courses",
    )

    title = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    is_published = models.BooleanField(default=False)

    # Textfields dont need max length
    description = models.TextField(blank=False, default="")

    promo_content = models.TextField(default="", blank=True)
    cover = models.ImageField(upload_to="covers/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if Course.objects.filter(slug=base_slug).exists():
                self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            else:
                self.slug = base_slug
        super().save(*args, **kwargs)

    class Meta:
        db_table = "courses_course"

    def __str__(self):
        return f"Course(title={self.title})"


class Module(models.Model):
    """
    Module that lessons are connected to. Not used in URL.
    Only used to group lessons in side-bar, ceration form, and
    analytics
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255, blank=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "courses_module"
        unique_together = [("course", "order")]
        # Always return in order by default
        ordering = ["order"]

    def __str__(self):
        return f"Module(course={self.course.title}), title={self.title})"

    def save(self, *args, **kwargs):
        # only on creation
        if not self.pk and not self.order:
            last = Module.objects.filter(course=self.course).aggregate(
                max_order=models.Max("order")
            )["max_order"] or 0
            self.order = last + 1
        super().save(*args, **kwargs)
        
class Enrollment(models.Model):
    """Connect user to course"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(auto_now=True)
    progress = models.PositiveSmallIntegerField(default=0)


    class Meta:
        db_table = "courses_enrollment"
        unique_together = [("user", "course")]

    def __str__(self):
        return f"Enrollment(user={self.user.email}, course={self.course.title})"
