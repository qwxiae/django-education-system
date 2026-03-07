from django.db import models
from apps.courses.models import Module
from django.urls import reverse 
import random

class Lesson(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    public_id = models.CharField(
        max_length=6,
        unique=True,
        editable=False
    )
    title = models.CharField(max_length=255, blank=False)
    is_published = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "lessons_lesson"
        unique_together = [
            ("module", "order")
        ]
        ordering = ['order']

    def save(self, *args, **kwargs):
        if not self.public_id:
            while True:
                candidate = str(random.randint(100_000, 999_999))
                if not Lesson.objects.filter(public_id=candidate).exists():
                    self.public_id = candidate
                    break
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("lessons:lesson", kwargs={"public_id": self.public_id})
    
    def __str__(self):
        return f"Lesson(Module{self.module.title}, {self.title})"
       
class Step(models.Model):
    class StepType(models.TextChoices):
        THEORY = 'T', 'Theory'
        CHOICE = 'C', 'Choice'
        TEXT_INPUT = 'I', 'Text Input'
        CODE = 'P', 'Programming'
    title = models.CharField(max_length=255)
    lesson = models.ForeignKey(
        Lesson,
        related_name="steps",
        on_delete=models.CASCADE
    )
    type = models.CharField(
        default=StepType.THEORY,
        choices=StepType,
        max_length=1
    )
    order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "lessons_step"
        unique_together = [
            ("lesson", "order"),
        ]
        ordering = ['order']

    def __str__(self):
        return f"Step(Lesson({self.lesson_id}), {self.order})"

class TheoryStep(Step):
    html_content = models.TextField()

    def save(self, *args, **kwargs):
        self.type = Step.StepType.THEORY
        super().save(*args, **kwargs)

    class Meta:
        db_table = "lessons_theorystep"

class ChoiceStep(Step):
    question_text = models.TextField()
    is_multiple = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.type = Step.StepType.CHOICE
        super().save(*args, **kwargs)
    

    class Meta:
        db_table = "lessons_choicestep"


class ChoiceOption(models.Model):
    step = models.ForeignKey(
        ChoiceStep,
        on_delete=models.CASCADE,
        related_name="options"
    )
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "lessons_choiceoption"
        unique_together = [
            ('step', 'order'),
        ]
        ordering = ["order"]

class TextInputStep(Step):
    question_text = models.TextField()
    answer = models.CharField(
        max_length=255,
        blank=False,
    )

    def save(self, *args, **kwargs):
        self.type = Step.StepType.TEXT_INPUT
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = "lessons_textinputstep"

class ProgrammingStep(Step):
    class ProgLang(models.TextChoices):
        PYTHON = 'py', 'Python'

    question_text = models.TextField()
    language = models.CharField(
        choices=ProgLang,
        default=ProgLang.PYTHON,
        max_length=6
    )
    time_limit_ms = models.PositiveIntegerField(default=5000)
    memory_limit_mb = models.PositiveIntegerField(default=50)
    solution_template = models.TextField(blank=True, default="")
    
    def save(self, *args, **kwargs):
        self.type = Step.StepType.CODE
        super().save(*args, **kwargs)

    class Meta:
        db_table = "lessons_programmingstep"

class TestCase(models.Model):
    step = models.ForeignKey(
        ProgrammingStep,
        on_delete=models.CASCADE,
        related_name="test_cases"
    )
    input_data = models.TextField()
    expected_output = models.TextField()
    order = models.PositiveSmallIntegerField()

    class Meta:
        db_table = "lessons_testcase"
        unique_together = [
            ('step', 'order')
        ]
        ordering = ["order"]
