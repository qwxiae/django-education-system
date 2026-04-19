import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command

from apps.core.utils import random_date_within_last_30_days
from apps.lessons.models import Step
from apps.submissions.models import Submission

User = get_user_model()

class Command(BaseCommand):
    help = "Create submissions for steps"

    def handle(self, *args, **kwargs):
        NEW_SUBMISSION_COUNT = 100
        call_command("seed_lessons")

        steps = Step.objects.filter(type__in=["C", "I", "P"])
        
        users = list(User.objects.filter(is_staff=False))

        for _ in range(NEW_SUBMISSION_COUNT):
            user = random.choice(users)
            enrollments = list(user.enrollments.select_related("course"))
            
            if not enrollments:
                return 
            
            enrollment = random.choice(enrollments)
            course = enrollment.course

            steps = Step.objects.filter(
                lesson__module__course=course,
                type__in=["C", "I", "P"],
            )

            if not steps.exists():
                continue

            step = random.choice(list(steps))
            
            submission, created = Submission.objects.get_or_create(
                user=user,
                step=step,
                defaults={
                    "status": random.choice(Submission.Status.values),
                },
            )

            if created:
                submission.submitted_at = random_date_within_last_30_days()
                submission.save(update_fields=["submitted_at"])

                self.stdout.write(
                    f"User {user.email}: step {step.id} ({course.title})"
                )

        self.stdout.write(self.style.SUCCESS("Done seeding submissions."))