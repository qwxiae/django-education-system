from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.courses.models import Course

from .forms import LoginForm, ProfileForm, RegisterForm, UserForm

User = get_user_model()


def register_view(request: HttpRequest) -> HttpResponse:
    """User register page: redirects to home when reigstered."""

    if request.user.is_authenticated:
        return redirect("users:profile")

    form = RegisterForm()

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # do not save RAW user, it will save password as plaintext
            user = form.save()

            login(request, user)
            return redirect("courses:home")

    return render(request, "users/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    """User login page: if user not found redirects to ?next or home page if query parameter does not exist."""

    if request.user.is_authenticated:
        return redirect("users:profile")

    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                next_url = (
                    request.POST.get("next")
                    or request.GET.get("next")
                    or "courses:home"
                )
                return redirect(next_url)
            else:
                # error must be present, so form can show it.
                form.add_error(None, "Invalid email or password")

    return render(
        request, "users/login.html", {"form": form, "next": request.GET.get("next", "")}
    )


def public_profile_view(request: HttpRequest, username: str) -> HttpResponse:
    """User's profile page: shows all user's created courses and information provided in profile form."""

    user = get_object_or_404(User, username=username)
    taught_courses = Course.objects.filter(
        author=user, is_published=True
    ).select_related("category")

    return render(
        request,
        "users/public_profile.html",
        {
            "profile_user": user,
            "taught_courses": taught_courses,
        },
    )


def logout_view(request: HttpRequest) -> HttpResponse:
    """Logout function: redirects to ?next or home is query parameter not provided."""

    if request.user.is_authenticated:
        logout(request)
    next_url = (
        request.GET.get("next") or request.META.get("HTTP_REFERER") or "courses:home"
    )
    return redirect(next_url)


@login_required
def profile_view(request: HttpRequest):
    """Authenticated users profile page: authenticated user's own profile."""

    return redirect("users:public_profile", username=request.user.username)


@login_required
def profile_edit_view(request: HttpRequest) -> HttpResponse:
    """Profile edit page: redirects to authenticated user's profile."""

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST,
            # for avatar upload
            request.FILES,
            instance=request.user.profile,
        )

        if user_form.is_valid() and profile_form.is_valid():
            profile_form.save()
            user_form.save()

            return redirect("users:public_profile", username=request.user.username)
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)

    return render(
        request,
        "users/profile_edit.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
        },
    )
