from django.urls import path

from . import views


app_name = "users"

urlpatterns = [
    # Auth
    path("auth/register/", views.register_view, name="register"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),


    # Public Profiles
    path("users/<str:username>/", views.public_profile_view, name="public_profile"),

    # Own Profile
    path("me/", views.profile_view, name="profile"),
    path("me/edit/", views.profile_edit_view, name="profile_edit"),
    
    # Password Reset
    # path("auth/password-reset/", views.password_reset_view, name="password_reset"),
    # path("auth/password-reset/confirm/", views.password_reset_confirm_view, name="password_reset_confirm"),

    # OAuth
    # path("auth/oauth/<str:provider>/", views.oauth_view, name="oauth"),
]