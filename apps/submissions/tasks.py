import subprocess
import tempfile
import os
from celery import shared_task
from django.utils import timezone

@shared_task(bind=True, max_retries=3)
def run_code_submission(self, code_submission_id):
    from .models import CodeSubmission, TestCaseResult
    from apps.lessons.models import ProgrammingStep

    try:
        code_sub = CodeSubmission.objects.select_related(
            "submission"
        ).get(pk=code_submission_id)

        prog_step = ProgrammingStep.objects.prefetch_related(
            "test_cases"
        ).get(pk=code_sub.submission.step_id)

        test_cases = prog_step.test_cases.all()
        passed = 0

        for test_case in test_cases:
            result = execute_python(
                code=code_sub.source_code,
                stdin=test_case.input_data,
                time_limit_ms=prog_step.time_limit_ms,
                memory_limit_mb=prog_step.memory_limit_mb,
            )

            is_passed = result["output"].strip() == test_case.expected_output.strip()
            if is_passed:
                passed += 1

            TestCaseResult.objects.create(
                submission=code_sub,
                test_case=test_case,
                passed=is_passed,
                actual_output=result["output"],
                runtime_ms=result["runtime_ms"],
                memory_mb=0,
            )

        code_sub.tests_passed = passed
        code_sub.tests_total = len(test_cases)
        code_sub.save()

        from .models import Submission
        submission = code_sub.submission
        submission.status = (
            Submission.Status.CORRECT
            if passed == len(test_cases)
            else Submission.Status.WRONG
        )
        submission.save()

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


def execute_python(code, stdin, time_limit_ms, memory_limit_mb):
    import time

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:
        f.write(code)
        tmp_path = f.name

    try:
        start = time.monotonic()
        result = subprocess.run(
            ["python", tmp_path],
            input=stdin or "",
            capture_output=True,
            text=True,
            timeout=time_limit_ms / 1000,
        )
        elapsed_ms = int((time.monotonic() - start) * 1000)

        return {
            "output": result.stdout,
            "error": result.stderr,
            "runtime_ms": elapsed_ms,
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Time limit exceeded",
            "runtime_ms": time_limit_ms,
        }
    finally:
        os.unlink(tmp_path)