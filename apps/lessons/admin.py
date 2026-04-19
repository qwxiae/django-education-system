from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from .models import (ChoiceOption, ChoiceStep, Lesson, ProgrammingStep, Step,
                     TestCase, TextInputStep, TheoryStep)


class StepInline(admin.TabularInline):
    model = Step
    extra = 1
    fields = ["title", "type", "order"]


class ChoiceOptionInline(admin.TabularInline):
    model = ChoiceOption
    extra = 2
    fields = ["text", "is_correct", "order"]


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1
    fields = ["input_data", "expected_output", "order"]


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "type", "order"]
    list_filter = ["type"]
    search_fields = ["title", "lesson__title"]

    readonly_fields = ["title", "lesson", "type", "order"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["public_id", "title", "module", "order", "is_published"]
    list_filter = ["is_published", "module__course"]
    search_fields = ["title", "module__title"]
    readonly_fields = ["public_id"]
    inlines = [StepInline]


@admin.register(TheoryStep)
class TheoryStepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "order"]
    search_fields = ["title"]
    fields = ["lesson", "title", "order", "html_content"]
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}


@admin.register(ChoiceStep)
class ChoiceStepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "order", "is_multiple"]
    search_fields = ["title"]
    fields = ["title", "lesson", "order", "question_text", "is_multiple"]
    inlines = [ChoiceOptionInline]
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}


@admin.register(ProgrammingStep)
class ProgrammingStepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "order", "language"]
    search_fields = ["title"]
    list_filter = ["language"]
    fields = [
        "lesson",
        "title",
        "order",
        "question_text",
        "language",
        "time_limit_ms",
        "memory_limit_mb",
        "solution_template",
    ]
    inlines = [TestCaseInline]


@admin.register(TextInputStep)
class TextInputStepAdmin(admin.ModelAdmin):
    list_display = ["title", "lesson", "order"]
    search_fields = ["title"]
    fields = ["title", "lesson", "order", "question_text", "answer"]
    formfield_overrides = {models.TextField: {"widget": TinyMCE()}}
