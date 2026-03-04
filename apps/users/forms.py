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
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "username": forms.TextInput(attrs={"placeholder": "johndoe"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # cant go into widgets as they are defined on UserCreationForm itself
        self.fields["password1"].widget.attrs["placeholder"] = "••••••••"
        self.fields["password2"].widget.attrs["placeholder"] = "••••••••"

class LoginForm(forms.Form):
    """
    Not a ModelForm - you are not creating/editing a model 
    but collecting credentials
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"})
    )

class ProfileForm(forms.ModelForm):
    # gets rid of checkbox; custom image upload in templates
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput()
    )
    class Meta:
        model = Profile
        fields = ["first_name", "last_name" , "avatar", "phone", "bio"]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username"]
