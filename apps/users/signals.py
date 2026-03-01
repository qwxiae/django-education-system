# apps/users/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile, Role, UserRole

User = get_user_model()

@receiver(post_delete, sender=Profile, dispatch_uid="delete_profile_avatar")
def delete_profile_avatar(sender, instance, **kwargs):
    """ Delete avatar from file system if avatar exists """
    if instance.avatar:
        instance.avatar.delete(save=False)
            
@receiver(post_save, sender=User, dispatch_uid="create_user_profile")
def create_user_profile(sender, instance, created, **kwargs):
    """ Create profile for user """
    '''
    # sender    # the model class that was saved → User
    # instance  # the actual object that was saved → the specific User row
    # created   # True if this was INSERT, False if this was UPDATE
    # kwargs    # extra stuff Django passes, you don't need it but must accept it
    '''
    # If created for the first time
    if created:
        Profile.objects.create(user=instance)
        # NotificationPreference.objects.create(user=instance)

        try:
            student_role = Role.objects.get(name="student")
            UserRole.objects.create(user=instance, role=student_role)
        except Exception as e:
            print(f"Signal error: {e}")