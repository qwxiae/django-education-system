import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.courses.models import Course, Enrollment, Module
from apps.lessons.models import (ChoiceStep, Lesson, ProgrammingStep, Step,
                                 TextInputStep, TheoryStep)
from apps.submissions.models import Submission

from .forms import (ChoiceOptionFormSet, ChoiceStepForm, CourseForm,
                    LessonForm, ModuleForm, ProgrammingStepForm,
                    TestCaseFormSet, TextInputStepForm, TheoryStepForm)


@login_required
def course_analytics_view(request, slug):
    course = get_object_or_404(
        Course, 
        slug=slug,
        # only the author can see the analytics
        author=request.user
    )

    # === Stats ===
    total_enrolled = Enrollment.objects.filter(course=course).count()

    avg_progress = Enrollment.objects.filter(
        course=course
    ).aggregate(avg=Avg("progress"))["avg"] or 0

    completed = Enrollment.objects.filter(
        course=course,
        progress=100
    ).count()

    thirty_days_ago = timezone.now() - timedelta(days=30)
    enrollments_by_day = (
        Enrollment.objects
        .filter(course=course, enrolled_at__gte=thirty_days_ago)
        .extra(select={"day": "DATE(enrolled_at)"})
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )

    # fill missing days with 0
    days_map = {str(e["day"]): e["count"] for e in enrollments_by_day}
    labels = []
    counts = []

    for i in range(30):
        day = (thirty_days_ago + timedelta(days=i)).strftime("%Y-%m-%d")
        labels.append(day)
        counts.append(days_map.get(day, 0))

    in_progress = Enrollment.objects.filter(
        course=course,
        progress__gt=0,
        progress__lt=100
    ).count()

    not_started = Enrollment.objects.filter(
        course=course,
        progress=0
    ).count()

    # Most failed steps
    failed_steps = (
        Submission.objects
        .filter(
            step__lesson__module__course=course,
            status=Submission.Status.WRONG
        )
        .values("step__title")
        .annotate(fail_count=Count("id"))
        .order_by("-fail_count")[:5]
    )
    completion_rate = round(completed / total_enrolled * 100) if total_enrolled else 0

    return render(request, "analytics/course_analytics.html", {
        "course": course,
        # stat cards
        "total_enrolled": total_enrolled,
        "avg_progress": round(avg_progress),
        "completed": completed,
        # line chart — JSON for Chart.js
        "chart_labels": json.dumps(labels),
        "chart_counts": json.dumps(counts),
        # doughnut chart
        "doughnut_data": json.dumps([completed, in_progress, not_started]),
        # failed steps table
        "failed_steps": failed_steps,
        "completion_rate": completion_rate,
    })

@login_required
def teach_dashboard_view(request):
    courses = Course.objects.filter(
        author=request.user
    ).annotate(
        enrollment_count=Count("enrollments"),
        avg_progress=Avg("enrollments__progress")
    ).order_by("-created_at")

    return render(request, "analytics/teach_dashboard.html", {
        "courses": courses,
    })


@login_required
def course_create_view(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.save()
            messages.success(request, "Course created")
            return redirect("analytics:course_edit", slug=course.slug)
    else:
        form = CourseForm()
    
    return render(request, "analytics/course_form.html", {
        "form": form,
        "title": "Create Course"
    })

@login_required
def course_edit_view(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated.")
            return redirect("analytics:course_edit", slug=course.slug)
    else:
        form = CourseForm(instance=course)
        
    modules = course.modules.prefetch_related("lessons").order_by("order")
    return render(request, "analytics/course_edit.html", {
        "form": form,
        "course": course,
        "modules": modules
    })
    
@login_required
def module_create_view(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    if request.method == "POST":
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, "Module created.")
            return redirect("analytics:course_edit", slug=course.slug)
    else:
        form = ModuleForm()
    return render(request, "analytics/module_form.html", {
        "form": form,
        "course": course,
        "title": "Add Module",
    })
    
@login_required
def module_edit_view(request, slug, module_id):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    module = get_object_or_404(Module, pk=module_id, course=course)

    if request.method == "POST":
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, "Module updated")
            return redirect("analytics:module_edit", slug=slug, module_id=module_id)
    else:
        form = ModuleForm(instance=module)

    lessons = module.lessons.order_by("order")
    return render(request, "analytics/module_edit.html", {
        "form": form,
        "course": course,
        "module": module,
        "lessons": lessons,
    })

@login_required
def lesson_create_view(request, slug, module_id):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    module = get_object_or_404(Module, pk=module_id, course=course)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, "Lesson created")
            return redirect("analytics:module_edit", slug=slug, module_id=module_id)
    else:
        form = LessonForm()
    
    return render(request, "analytics/lesson_form.html", {
        "form": form,
        "course": course,
        "module": module,
        "title": "Add Lesson"
    })

@login_required
def lesson_edit_view(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        public_id=lesson_id
    )
    course = lesson.module.course

    if course.author != request.user:
        return redirect("analytics:teach_dashboard")
    
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, "Lesson updated.")
            return redirect("analytics:lesson_edit", lesson_id=lesson_id)
    else:
        form = LessonForm(instance=lesson)

    steps = lesson.steps.order_by("order")

    return render(request, "analytics/lesson_edit.html", {
        "form": form,
        "course": course,
        "lesson": lesson,
        "steps": steps,
    })

@login_required
def step_create_view(request, lesson_id):
    lesson = get_object_or_404(
        Lesson.objects.select_related("module__course"),
        public_id=lesson_id
    )
    course = lesson.module.course
    if course.author != request.user:
        return redirect("analytics:teach_dashboard")
    
    step_type = request.GET.get("type", "T")
    form_map = {
        "T": TheoryStepForm,
        "C": ChoiceStepForm,
        "I": TextInputStepForm,
        "P": ProgrammingStepForm,
    }
    FormClass = form_map.get(step_type, TheoryStepForm)

    if request.method == "POST":
        form = FormClass(request.POST)
        formset = None

        if step_type == "C":
            formset = ChoiceOptionFormSet(request.POST)
        elif step_type == "P":
            formset = TestCaseFormSet(request.POST)

        if form.is_valid() and (formset is None or formset.is_valid()):
            step = form.save(commit=False)
            step.lesson = lesson 
            step.save()

            if formset:
                formset.instance = step
                formset.save()

            messages.success(request, "Step created.")
            return redirect("analytics:lesson_edit", lesson_id=lesson_id)
    else:
        form = FormClass()
        formset = None
        if step_type == "C":
            formset = ChoiceOptionFormSet()
        elif step_type == "P":
            formset = TestCaseFormSet()

    return render(request, "analytics/step_form.html", {
        "form": form,
        "formset": formset,
        "step_type": step_type,
        "lesson": lesson,
        "course": course,
        "title": "Add Step",
    })

@login_required
def step_edit_view(request, step_id):
    step = get_object_or_404(Step, pk=step_id)
    lesson = step.lesson
    course = lesson.module.course

    if course.author != request.user:
        return redirect("analytics:teach_dashboard")
    
    form_map = {
        "T": (TheoryStepForm, TheoryStep, None),
        "C": (ChoiceStepForm, ChoiceStep, ChoiceOptionFormSet),
        "I": (TextInputStepForm, TextInputStep, None),
        "P": (ProgrammingStepForm, ProgrammingStep, TestCaseFormSet),
    }
    FormClass, ModelClass, FormSetClass = form_map[step.type]
    instance = get_object_or_404(ModelClass, pk=step.pk)

    if request.method == "POST":
        form = FormClass(request.POST, instance=instance)
        formset = FormSetClass(request.POST, instance=instance) if FormSetClass else None

        if form.is_valid() and (formset is None or formset.is_valid()):
            form.save()
            if formset:
                formset.save()
            messages.success(request, "Step updated.")
            return redirect("analytics:step_edit", step_id=step_id)
    else:
        form = FormClass(instance=instance)
        formset = FormSetClass(instance=instance) if FormSetClass else None

    return render(request, "analytics/step_form.html", {
        "form": form,
        "formset": formset,
        "step_type": step.type,
        "lesson": lesson,
        "course": course,
        "step": instance,
        "title": "Edit Step",
    })