from django.contrib.auth import get_user_model
from django.db import models

from apps.lessons.models import Step, TestCase

User = get_user_model()


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "P", "Pending"
        CORRECT = "C", "Correct"
        WRONG = "W", "Wrong"

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="submissions"
    )
    step = models.ForeignKey(Step, on_delete=models.CASCADE, related_name="submissions")
    status = models.CharField(choices=Status, max_length=1, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "submissions_submission"
        ordering = ["-submitted_at"]
        # you'll query most: "did this user submit this step?"
        indexes = [models.Index(fields=["user", "step"])]

    def __str__(self):

        return f"Submission(user={self.user_id}, step={self.step_id})"


class ChoiceSubmission(models.Model):
    # each attempt is new, this does not mean that one step has one attempt
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="choice_submission"
    )
    selected_options = models.ManyToManyField(
        "lessons.ChoiceOption", related_name="submissions"
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "submissions_choicesubmissions"


class TextSubmission(models.Model):
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="text_submission"
    )
    answer_text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = "submissions_textsubmissions"


class CodeSubmission(models.Model):
    submission = models.OneToOneField(
        Submission, on_delete=models.CASCADE, related_name="code_submission"
    )
    source_code = models.TextField()
    tests_passed = models.PositiveSmallIntegerField(default=0)
    tests_total = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "submissions_codesubmissions"


class TestCaseResult(models.Model):
    """Each TestCase run produces one result"""

    # one code submission has MANY test case results
    submission = models.ForeignKey(
        CodeSubmission, on_delete=models.CASCADE, related_name="test_results"
    )
    test_case = models.ForeignKey(
        TestCase, on_delete=models.CASCADE, related_name="results"
    )
    passed = models.BooleanField(default=False)
    actual_output = models.TextField()
    runtime_ms = models.PositiveSmallIntegerField(default=0)
    memory_mb = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = "submissions_testcasesubmissions"
        # dont run same test twice per using submission
        unique_together = [("submission", "test_case")]
        ordering = ["test_case__order"]
