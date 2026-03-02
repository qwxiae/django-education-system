from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager



class UserManager(BaseUserManager):
    """Logging using email."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Remove names - they live on Profile
    first_name = None
    last_name = None

    username = models.CharField(
        max_length=50,
        unique=True,
        null=False,
        blank=True
    )
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()


    def has_role(self, role_name: str) -> bool:
        return self.user_roles.filter(role__name=role_name).exists()
    
    # Properties are needed since methods cannot be used in templates
    @property
    def is_student(self) -> bool:
        return self.has_role("student")
    
    @property
    def is_instructor(self) -> bool:
        return self.has_role("instructor")
    
    @property
    def is_moderator(self) -> bool:
        return self.has_role("moderator")                

    class Meta:
        db_table = "users_user"

    def __str__(self):
        return self.email or "No email"


class Profile(models.Model):
    """First name and last name are stored in user. Additional fields here."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        default=""
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        default=""
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        default=""
    )

    class Meta:
        db_table = "users_profile"

    def __str__(self):
        return f"Profile({self.user.email})"
    

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=False)
    description = models.TextField(max_length=500, blank=True, default="")

    class Meta:
        db_table = "users_role"

    def __str__(self):
        return self.name 
    

class UserRole(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles"
    )
    # PROTECT because otherwise deleting a User will delete a Role
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="user_roles"
    )

    class Meta:
        db_table = "users_userrole"
        # prevents duplicate assignments
        unique_together = [("user", "role")]

# class OAuthConnection(models.Model):
#     PROVIDER_CHOICES = [
#         ("google", "Google"),
#         ("github", "GitHub"),
#     ]

#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="oauth_connections",
#     )

#     provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
#     provider_user_id = models.CharField(max_length=255)
#     provider_email = models.EmailField(blank=True, default="")
#     connected_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = "users_oauthconnection"
#         unique_together = [("user", "provider")]

#     def __str__(self):
#         return f"{self.user.email} via {self.provider}"
    

