from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

from apps.courses.models import Course, Module
from apps.lessons.models import (ChoiceOption, ChoiceStep, Lesson,
                                 ProgrammingStep, TestCase, TextInputStep,
                                 TheoryStep)


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "category",
            "description",
            "promo_content",
            "cover",
            "is_published"
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "promo_content": TinyMCE()
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ["title"]

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "is_published"]

class TheoryStepForm(forms.ModelForm):
    class Meta:
        model = TheoryStep
        fields = ["title", "html_content"]
        widgets = {
            "html_content": TinyMCE()
        }

class ChoiceStepForm(forms.ModelForm):
    class Meta:
        model = ChoiceStep
        fields = ["title", "question_text", "is_multiple"]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3}),
        }

class ChoiceOptionForm(forms.ModelForm):
    class Meta:
        model = ChoiceOption
        fields = ["text", "is_correct", "order"]

ChoiceOptionFormSet = inlineformset_factory(
    ChoiceStep,
    ChoiceOption,
    form=ChoiceOptionForm,
    extra=2,
    can_delete=True,
)

class TextInputStepForm(forms.ModelForm):
    class Meta:
        model = TextInputStep
        fields = ["title", "question_text", "answer"]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3})
        }

class ProgrammingStepForm(forms.ModelForm):
    class Meta:
        model = ProgrammingStep
        fields = [
            "title", "question_text", "language",
            "time_limit_ms", "memory_limit_mb", "solution_template"
        ]
        widgets = {
            "question_text": forms.Textarea(attrs={"rows": 3}),
            "solution_template": forms.Textarea(attrs={
                "rows": 8, "class": "code-editor"})
        }

TestCaseFormSet = inlineformset_factory(
    ProgrammingStep,
    TestCase,
    fields=["input_data", "expected_output", "order"],
    extra=1,
    can_delete=True,
)