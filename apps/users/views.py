from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, ProfileForm, RegisterForm,UserForm
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from apps.courses.models import Course

User = get_user_model()


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("users:profile")
    
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Do not save RAW user, it will save password as plaintext
            user = form.save()

            login(request, user)
            return redirect('courses:home')

    return render(request, "users/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("users:profile")
    
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                next_url = request.POST.get("next") or request.GET.get("next") or "courses:home"
                return redirect(next_url)
            else:
                # Make sure error is present, so form can show it.
                form.add_error(None, "Invalid email or password")

    return render(request, "users/login.html", {
        "form": form,
        "next": request.GET.get("next", "")
        }
    )


def public_profile_view(request: HttpRequest, username: str) -> HttpResponse:
    user = get_object_or_404(User, username=username)
    taught_courses = Course.objects.filter(
        author=user,
        is_published=True
    )
    return render(request, "users/public_profile.html", {
        "profile_user": user,
        "taught_courses": taught_courses,
    })
    # return render(request, "users/public_profile.html", {"profile_user": user})
    # user = get_object_or_404(User, pk=user_id)


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "courses:home"
    return redirect(next_url)


@login_required
def profile_view(request: HttpRequest):
    return redirect("users:public_profile", username=request.user.username)


@login_required
def profile_edit_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # we do not want to create a new profile but update => must pass instance  
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST,
            # for avatar upload
            request.FILES,
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            profile_form.save()
            user_form.save()
            
            return redirect('users:profile')
        
    user_form = UserForm(instance=request.user) 
    profile_form  = ProfileForm(instance=request.user.profile)

    return render(request, "users/profile_edit.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })
