from django.core.management import BaseCommand, call_command

from apps.courses.models import Course, Module
from apps.lessons.models import (ChoiceOption, ChoiceStep, Lesson,
                                 ProgrammingStep, TestCase, TextInputStep,
                                 TheoryStep)


class Command(BaseCommand):
    help = "Seed lessons for all courses"

    def handle(self, *args, **kwargs):
        call_command("seed_courses")

        courses = Course.objects.all()

        for course in courses:
            self.stdout.write(f"\n=== Processing course: {course.title} ===")

            modules = Module.objects.filter(course=course).order_by("order")

            for module in modules:
                self.stdout.write(f"  -> Module: {module.title}")

                for i in range(1, 5):
                    lesson, created = Lesson.objects.get_or_create(
                        module=module,
                        order=i,
                        defaults={
                            "title": f"{module.title} — Lesson {i}",
                            "is_published": True,
                        },
                    )

                    if not created:
                        continue

                    self.stdout.write(f"    [created] {lesson.title}")

                    # === STEP 1: THEORY ===
                    TheoryStep.objects.get_or_create(
                        lesson=lesson,
                        order=1,
                        defaults={
                            "title": "Theory",
                            "html_content": f"<p>This is theory for {lesson.title}</p>",
                        },
                    )

                    # === STEP 2: QUIZ ===
                    choice, _ = ChoiceStep.objects.get_or_create(
                        lesson=lesson,
                        order=2,
                        defaults={
                            "title": "Quick Quiz",
                            "question_text": "Pick the correct answer",
                        }
                    )

                    for idx, (text, correct) in enumerate(
                        [
                            ("Correct answer", True),
                            ("Wrong answer 1", False),
                            ("Wrong answer 2", False),
                            ("Wrong answer 3", False),
                        ],
                        start=1,
                    ):
                        ChoiceOption.objects.get_or_create(
                            step=choice,
                            order=idx,
                            defaults={
                                "text": text,
                                "is_correct": correct,
                            }
                        )

                    # === STEP 3: TEXT INPUT ===
                    TextInputStep.objects.get_or_create(
                        lesson=lesson,
                        order=3,
                        defaults={
                            "title": "Fill in the blank",
                            "question_text": "2 + 2 = ?",
                            "answer": "4",
                        }
                        
                    )

                    # === STEP 4: PROGRAMMING ===
                    if course.slug in ["introduction-to-python"]:
                        prog, _ = ProgrammingStep.objects.get_or_create(
                            lesson=lesson,
                            order=4,
                            defaults = {
                                "title": "Coding Task",
                                "question_text": "Print: Hello, World!",
                                "language": ProgrammingStep.ProgLang.PYTHON,
                                "solution_template": "# Write your code here\n",
                            }
                        )

                        TestCase.objects.get_or_create(
                            step=prog,
                            order=1,
                            defaults={"input_data": "", "expected_output": "Hello, World!"}
                        )

        self.stdout.write(self.style.SUCCESS("\n✅ Done seeding ALL lessons"))


        if created:
            TestCase.objects.get_or_create(
                step=prog,
                order=1,
                defaults={"input_data": "", "expected_output": "Hello, World!"},
            )
