from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string
from apps.lessons.models import Step, ChoiceStep, TextInputStep, ProgrammingStep
from .models import Submission, ChoiceSubmission, TextSubmission, CodeSubmission

@login_required
@require_POST
def submit_view(request, lesson_id):
    step_id = request.POST.get("step_id")
    step = get_object_or_404(Step, pk=step_id)

    # base submission
    submission = Submission.objects.create(
        user=request.user,
        step=step,
        status=Submission.Status.PENDING
    )

    if step.type == Step.StepType.TEXT_INPUT:
        text_step = get_object_or_404(TextInputStep, pk=step.pk)
        answer = request.POST.get('answer', "").strip().lower()
        is_correct = answer == text_step.answer.strip().lower()

        TextSubmission.objects.create(
            submission=submission,
            answer_text=answer,
            is_correct=is_correct
        )

        submission.status = Submission.Status.CORRECT if is_correct else Submission.Status.WRONG
        submission.save()

        return render(request, "partials/submission_result.html", {
            "is_correct": is_correct,
            "correct_answer": text_step.answer if not is_correct else None,
            "step": text_step,
            "lesson_id": lesson_id,
        })

    elif step.type == Step.StepType.CHOICE:
        choice_step = get_object_or_404(
            ChoiceStep.objects.prefetch_related("options"),
            pk=step.pk
        )

        selected_ids = request.POST.getlist("answer")

        selected_options = choice_step.options.filter(pk__in=selected_ids)
        correct_options = choice_step.options.filter(is_correct=True)

        is_correct = (
            set(selected_options.values_list("pk", flat=True)) ==
            set(correct_options.values_list("pk", flat=True))
        )

        choice_sub = ChoiceSubmission.objects.create(
            submission=submission,
            is_correct=is_correct
        )
        choice_sub.selected_options.set(selected_options)

        submission.status = Submission.Status.CORRECT if is_correct else Submission.Status.WRONG
        submission.save()

        return render(request, "partials/submission_result.html", {
            "is_correct": is_correct,
            "correct_options": correct_options if not is_correct else None,
            "step": choice_step,
            "lesson_id": lesson_id,
        })
    
    elif step.type == Step.StepType.CODE:
        prog_step = get_object_or_404(ProgrammingStep, pk=step.pk)
        source_code = request.POST.get("code", "")

        code_sub = CodeSubmission.objects.create(
            submission=submission,
            source_code=source_code,
            tests_total=prog_step.test_cases.count()
        )

        return render(request, "partials/submission_result.html", {
            "is_correct": None,  # pending
            "pending": True,
            "submission_id": submission.pk,
            "step": prog_step,
            "lesson_id": lesson_id,
        })

    return HttpResponse(status=400)

# submit answer, poll result
def attempts_list(request):
    pass

def attempt_detail(request):
    pass