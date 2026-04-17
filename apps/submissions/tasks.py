import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
import logging

logging.getLogger()

def execute_with_piston(source_code, stdin="", language="python", version="3.10.0"):
    try:
        response = requests.post(
            f"{settings.PISTON_URL}/api/v2/execute",
            json={
                "language": language,
                "version": version,
                "files": [{"content": source_code}],
                "stdin": stdin or "",
                "run_timeout": 3000,        # 3 sec - how long can code be run inside Piston
                "compile_timeout": 10000,
                "run_memory_limit": 128 * 1024 * 1024, # 128MB max
            },
            timeout=15  # HTTP request timeout; how long to wait for piston to reply
        )
        logging.info("PISTON RAW RESPONSE:", response.text)
        response.raise_for_status()
        data = response.json()
        run = data.get("run", {})

        return {
            "output": run.get("stdout", ""),
            "error": run.get("stderr", ""),
            "runtime_ms": int(float(run.get("cpu_time", 0)) * 1000),
            "timed_out": run.get("code") == 124,  # 124 = timeout exit code
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
    from .models import CodeSubmission, TestCaseResult, Submission
    from apps.lessons.models import ProgrammingStep

    try:
        code_sub = CodeSubmission.objects.select_related(
            "submission"
        ).get(pk=code_submission_id)

        prog_step = ProgrammingStep.objects.prefetch_related(
            "test_cases"
        ).get(pk=code_sub.submission.step_id)

        test_cases = list(prog_step.test_cases.all())
        passed = 0

        for test_case in test_cases:
            result = execute_with_piston(
                source_code=code_sub.source_code,
                stdin=test_case.input_data,
            )

            # normalize output for comparison
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
                }
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