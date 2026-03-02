from django.shortcuts import render, redirect, get_object_or_404
from .forms import LoginForm, ProfileForm, RegisterForm
from django.http import HttpRequest, HttpResponse, Http404, JsonResponse
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required

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
    profile = user.profile
    data = {
        "username": user.username,
        "email": profile.user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "bio": profile.bio,
        "phone": profile.phone,
        "avatar": profile.avatar.url if profile.avatar else None,
    }

    return JsonResponse(data)
    # return render(request, "users/public_profile.html", {"profile_user": user})
    # user = get_object_or_404(User, pk=user_id)


def logout_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "courses:home"
    return redirect(next_url)


@login_required
def profile_view(request: HttpRequest):
    profile = request.user.profile
    
    data = {
        "username": request.user.username,
        "email": profile.user.email,
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "bio": profile.bio,
        "phone": profile.phone,
        "avatar": profile.avatar.url if profile.avatar else None,
    }
    
    return JsonResponse(data)
    # return render(
    #     request, "users/profile.html",
    #     # get all the data directly, no need to query
    #     {"profile": request.user.profile}
    # )


@login_required
def profile_edit_view(request: HttpRequest) -> HttpResponse:
    form = ProfileForm()

    if request.method == 'POST':
        # Must have request.FILES for avatar upload
        # Must pass instance otherwise new profile will be created
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, "users/profile_edit.html", {"form": form})
