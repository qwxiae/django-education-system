from django.core.management import BaseCommand, call_command
from django.contrib.auth import get_user_model
from apps.courses.models import Category, Course, Module, Enrollment
from django.utils.text import slugify
import random
from datetime import timedelta
from django.utils import timezone

def random_date_within_last_30_days():
    now = timezone.now()
    delta = timedelta(days=random.randint(0, 30),
                      seconds=random.randint(0, 86400))
    return now - delta

User = get_user_model()


class Command(BaseCommand):
    help = "Create default courses"

    def handle(self, *args, **kwargs):
        call_command("seed_roles")
        call_command("seed_categories")
        call_command("seed_users")

        user_instuctor = User.objects.get(email="janedoe@test.com")
        category1 = Category.objects.get(slug="mathematics")
        category2 = Category.objects.get(slug="programming")

        course_data = [
            (
                user_instuctor,
                category1,
                "Algebra I",
                True,
                ["Introduction", "Linear Equations"],
            ),
            (user_instuctor, category1, "Algebra II", True, ["Quadratics"]),
            (
                user_instuctor,
                category2,
                "Introduction to Python",
                True,
                ["Getting Started", "Data Types", "Functions"],
            ),
            (
                user_instuctor,
                category2,
                "Introduction to Java",
                False,
                ["Getting Started", "Data Types", "Functions"],
            ),
        ]

        for user, category, title, is_published, module_titles in course_data:
            slug = slugify(title)
            course, created = Course.objects.get_or_create(
                slug=slug,
                defaults={
                    "author": user,
                    "title": title,
                    "category": category,
                    "is_published": is_published,
                },
            )
            if created:
                self.stdout.write(f"Created course: {course}")
                for order, module_title in enumerate(module_titles, start=1):
                    Module.objects.get_or_create(
                        course=course, order=order, defaults={"title": module_title}
                    )
            else:
                self.stdout.write(f"Course '{course}' already exists")

        self.stdout.write(self.style.SUCCESS("Done creating courses."))


        course = Course.objects.get(slug="introduction-to-python")
        users = User.objects.filter(is_staff=False)

        NEW_TEST_USERS = 30
        if users.count() < NEW_TEST_USERS:
            self.stdout.write("Not enough users — creating test students")
            for i in range(NEW_TEST_USERS):
                user, created = User.objects.get_or_create(
                    email=f"student{i}@test.com",
                    defaults={
                        "username": f"student{i}",
                        "is_active": True,
                    }
                )
                if created:
                    user.set_password("testpass123")
                    user.save()

            users = User.objects.filter(is_staff=False)

        for user in users:
            enrollment, created = Enrollment.objects.get_or_create(
                user=user,
                course=course,
                defaults={"progress": random.randint(0, 100)}
            )

            enrollment.progress = random.randint(0, 100)
            enrollment.enrolled_at = random_date_within_last_30_days()

            enrollment.save(update_fields=["progress", "enrolled_at"])

            self.stdout.write(
                f"Enrolled {user.email} with progress {enrollment.progress}%"
            )

        self.stdout.write(self.style.SUCCESS("Done seeding enrollments."))