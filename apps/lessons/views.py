from django.shortcuts import get_object_or_404, render

from .models import (ChoiceStep, Lesson, ProgrammingStep, Step, TextInputStep,
                     TheoryStep)


def lesson_view(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        public_id=lesson_id,
        is_published=True,
    )
    steps = lesson.steps.all()
    step_order = request.GET.get("step", 1)
    current_step = get_object_or_404(Step, lesson=lesson, order=step_order)

    step_content = None
    if current_step.type == "T":
        step_content = TheoryStep.objects.get(pk=current_step.pk)
    elif current_step.type == "C":
        step_content = ChoiceStep.objects.prefetch_related("options").get(pk=current_step.pk)
    elif current_step.type == "I":
        step_content = TextInputStep.objects.get(pk=current_step.pk)
    elif current_step.type == "P":
        step_content = ProgrammingStep.objects.prefetch_related("test_cases").get(pk=current_step.pk)

    # TODO: sessions vs query
    completed_steps = request.session.get("completed_steps")

    return render(request, "lessons/lesson.html", {
        "lesson": lesson,
        "course": lesson.module.course,
        "steps": steps,
        "current_step": step_content,
        "completed_steps": completed_steps,
    })

