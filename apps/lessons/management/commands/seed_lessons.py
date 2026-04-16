from apps.lessons.models import (
    Lesson,
    TheoryStep,
    ChoiceStep,
    ChoiceOption,
    TextInputStep,
    ProgrammingStep,
    TestCase,
)

from apps.courses.models import Course, Module
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = "Create lessons in modules for courses"

    def handle(self, *args, **kwargs):
        call_command("seed_courses")

        course = Course.objects.get(slug="introduction-to-python")
        m1 = Module.objects.get(course=course, order=1)

        lesson_data = [
            (m1, "About this course", 1, True),
            (m1, "Data types in Python", 2, True),
            (m1, "Quick Test", 3, True),
        ]

        lessons = {}

        for module, title, order, is_published in lesson_data:
            lesson, created = Lesson.objects.get_or_create(
                module=module,
                order=order,
                defaults={"title": title, "is_published": is_published},
            )

            status = "created" if created else "exists"
            self.stdout.write(f"[{status}] {title}")
            lessons[title] = lesson

        # == Creating Steps ==

        # Lesson 1 - About this course
        about = lessons["About this course"]
        # step 1 - theory
        TheoryStep.objects.get_or_create(
            lesson=about,
            order=1,
            defaults={
                "title": "Introduction",
                "html_content": "<p>Welcome to Introduction to Python.</p>",
            },
        )
        # step 2 - theory
        TheoryStep.objects.get_or_create(
            lesson=about,
            order=2,
            defaults={
                "title": "Prerequisites",
                "html_content": "<p>Basic arithmetic is all you need.</p>",
            },
        )
        # step 3 - [rogramming]
        prog, created = ProgrammingStep.objects.get_or_create(
            lesson=about,
            order=3,
            defaults={
                "title": "Hello World",
                "question_text": "Write a program that prints 'Hello, World'",
                "language": ProgrammingStep.ProgLang.PYTHON,
                "solution_template": "# Write your solution here\n",
            },
        )

        if created:
            TestCase.objects.get_or_create(
                step=prog,
                order=1,
                defaults={"input_data": "", "expected_output": "Hello, World!"},
            )

        # Lesson 2 - Data types in python
        data = lessons["Data types in Python"]
        # step 1 - theory
        TheoryStep.objects.get_or_create(
            lesson=data,
            order=1,
            defaults={
                "title": "Mutable vs Immutable",
                "html_content": "<p>Immutable: int, str, \
                tuple. Mutable: list, dict, set.</p>",
            },
        )

        # 2 - text input
        TextInputStep.objects.get_or_create(
            lesson=data,
            order=2,
            defaults={
                "title": "Fill in the blank: ",
                "question_text": "Bool is subclass of _____?",
                "answer": "int",
            },
        )

        # Lesson 3 - Quick test
        test = lessons["Quick Test"]
        choice, created = ChoiceStep.objects.get_or_create(
            lesson=test,
            order=1,
            defaults={
                "title": "Pick the correct answer: ",
                "question_text": "Which data type is immutable?",
            },
        )

        if created:
            for order, text, correct in [
                (1, "int", True),
                (2, "dict", False),
                (3, "list", False),
                (4, "set", False),
            ]:
                ChoiceOption.objects.get_or_create(
                    step=choice,
                    order=order,
                    defaults={"text": text, "is_correct": correct},
                )

        self.stdout.write(self.style.SUCCESS("Done seeding lessons."))
