from django import forms
from .models import User, Profile 
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    """ 
    UserCreationForm handles password1, password2, hashing. 
    Tell the form to use email instead of username for auth
    """
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class LoginForm(forms.Form):
    """
    Not a ModelForm - you are not creating/editing a model 
    but collecting credentials
    """
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


# == Update FORMS ==
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name" , "avatar", "phone", "bio"]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]

# TODO: Email forms
# class EmailChangeForm
# class PasswordChangeForm