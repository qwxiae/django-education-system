from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    """We owerite the default username authentication"""
    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        # Django admin login form sends credentials as username=
        # your login form sends them as email=
        """
        if email is None:
            email = kwargs.get("username")

        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
        
        except User.DoesNotExist:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None
    