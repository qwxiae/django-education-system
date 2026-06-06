import logging

import requests
from celery import shared_task
from django.conf import settings

logger = logging.getLogger()


def execute_code(source_code, stdin="", timeout_ms=5000):
    try:
        response = requests.post(
            f"{settings.EXECUTOR_URL}/execute",
            json={
                "source_code": source_code,
                "stdin": stdin or "",
                "timeout_ms": timeout_ms,
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "output": data.get("stdout", ""),
            "error": data.get("stderr", ""),
            "runtime_ms": data.get("runtime_ms", 0),
            "timed_out": data.get("timed_out", False),
        }
    except requests.RequestException as e:
        return {
            "output": "",
            "error": f"Execution service unavailable: {str(e)}",
            "runtime_ms": 0,
            "timed_out": False,
        }


@shared_task(bind=True, max_retries=3)
def run_code_submission(self, code_submission_id):
    from apps.lessons.models import ProgrammingStep

    from .models import CodeSubmission, Submission, TestCaseResult

    try:
        code_sub = CodeSubmission.objects.select_related("submission").get(
            pk=code_submission_id
        )

        prog_step = ProgrammingStep.objects.prefetch_related("test_cases").get(
            pk=code_sub.submission.step_id
        )

        test_cases = list(prog_step.test_cases.all())
        passed = 0

        for test_case in test_cases:
            result = execute_code(
                source_code=code_sub.source_code,
                stdin=test_case.input_data,
                timeout_ms=prog_step.time_limit_ms,
            )

            actual = result["output"].strip()
            expected = test_case.expected_output.strip()
            is_passed = actual == expected and not result["timed_out"]

            if is_passed:
                passed += 1

            TestCaseResult.objects.update_or_create(
                submission=code_sub,
                test_case=test_case,
                defaults={
                    "passed": is_passed,
                    "actual_output": result["output"] or result["error"],
                    "runtime_ms": result["runtime_ms"],
                },
            )

        code_sub.tests_passed = passed
        code_sub.tests_total = len(test_cases)
        code_sub.save()

        submission = code_sub.submission
        submission.status = (
            Submission.Status.CORRECT
            if passed == len(test_cases)
            else Submission.Status.WRONG
        )
        submission.save()

    except CodeSubmission.DoesNotExist as exc:
        raise self.retry(exc=exc, countdown=5)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
