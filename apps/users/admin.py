from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, Role, UserRole

class UserRoleInline(admin.TabularInline):
    model = UserRole
    # one empty row for adding a role
    extra = 1

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]
    search_fields = ["name"]

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["username", "email", "is_staff", "is_active", "date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": (
            "is_active",
            "is_staff", 
            "is_superuser",
            "groups",
            "user_permissions",
        )}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email" "password1", "password2", "is_staff", "is_superuser"),
        }),
    )

    search_fields = ["username", "email"]
    readonly_fields = ["last_login", "date_joined"]
    inlines = [UserRoleInline]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "avatar", "phone", "bio"]
    fieldsets = (
        (None, {"fields": ("user", "avatar", "bio")}),
        ("Personal Information", {"fields": ("first_name", "last_name", "phone")})
    )
    search_fields = ["user", "user__email"]

# @admin.register(OAuthConnection)
# class OAuthConnectionAdmin(admin.ModelAdmin):
#     list_display = ["user", "provider", "provider_email", "connected_at"]
#     search_fields = ["user__email", "provider_email"]
#     list_filter = ["provider"]