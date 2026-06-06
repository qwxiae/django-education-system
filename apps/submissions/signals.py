from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.courses.models import Enrollment
from apps.lessons.models import Step

from .models import Submission


@receiver(post_save, sender=Submission)
def update_enrollment_progress(sender, instance, created, **kwargs):
    if instance.status != Submission.Status.CORRECT:
        return

    if instance.step.type not in ["C", "I", "P"]:
        return

    try:
        enrollment = Enrollment.objects.get(
            user=instance.user, course=instance.step.lesson.module.course
        )
    except Enrollment.DoesNotExist:
        return

    previous_correct = (
        Submission.objects.filter(
            user=instance.user, step=instance.step, status=Submission.Status.CORRECT
        )
        .exclude(pk=instance.pk)
        .exists()
    )

    if not previous_correct:
        from django.db.models import F

        enrollment.progress = F("progress") + 1
        enrollment.save()
        enrollment.refresh_from_db()
        enrollment.last_active_at = instance.submitted_at
        enrollment.save()
