from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Course

User = get_user_model()


@receiver(post_delete, sender=Course, dispatch_uid="delete_course_promo")
def delete_course_promo(sender, instance, **kwargs):
    if instance.cover:
        # no need to save as instance will be deleted
        instance.cover.delete(save=False)
