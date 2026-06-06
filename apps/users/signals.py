# apps/users/signals.py
from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Profile, Role, UserRole

User = get_user_model()


@receiver(post_delete, sender=Profile, dispatch_uid="delete_profile_avatar")
def delete_profile_avatar(sender, instance, **kwargs):
    """Delete avatar from file system if avatar exists"""

    if instance.avatar:
        instance.avatar.delete(save=False)


@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile for user"""

    # If created for the first time
    if created:
        Profile.objects.create(user=instance)
        # NotificationPreference.objects.create(user=instance)

        try:
            student_role = Role.objects.get(name="student")
            UserRole.objects.create(user=instance, role=student_role)
        except Exception as e:
            print(f"Signal error: {e}")
