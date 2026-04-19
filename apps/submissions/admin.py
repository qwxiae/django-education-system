from django.contrib import admin

from .models import (ChoiceSubmission, CodeSubmission, Submission,
                     TestCaseResult, TextSubmission)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'step', 'status', 'submitted_at']
    search_fields = ['user__email', 'user__username', 'step__title']
    ordering = ['-submitted_at']
    list_filter = ['status']

@admin.register(ChoiceSubmission)
class ChoiceSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'is_correct']
    search_fields = ['submission']
    list_filter = ['is_correct']

@admin.register(TextSubmission)
class TextSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'answer_text', 'is_correct']
    search_fields = ['submission']
    list_filter = ['is_correct']
    
@admin.register(CodeSubmission)
class CodeSubmissionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'tests_passed', 'tests_total']
    search_fields = ['submission']

@admin.register(TestCaseResult)
class TestCaseResultAdmin(admin.ModelAdmin):
    list_display = ['submission', 'test_case', 'passed', 'runtime_ms', 'memory_mb']
    search_fields = ['submission', 'test_case']
    list_filter = ['passed']