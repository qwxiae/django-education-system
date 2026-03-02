from django.core.management import BaseCommand, call_command
from apps.users.models import Role, User, UserRole

class Command(BaseCommand):
    help = "Create default users"

    def handle(self, *args, **kwargs):
        call_command("seed_roles")



        instructor_role = Role.objects.get(name="instructor")
        user_data = [
            ("test_user", "test@test.com", "hr2htBeTryYQ", True),
            ("jane_doe", "janedoe@test.com", "madotsuki", True),
            ("john_d0e", "johndoe@test.com", "urotsuki", False),
            ("annabe113", "annabelle@test.com", "PXQENDSEDTkr", False),
            ("nadine_rami", "nadinerami@test.com", "NWyhpcVtF6rp", False)
        ]

        for username, email, password, is_instructor in user_data:
            user, create = User.objects.get_or_create(
                username=username,
                email=email,
                defaults={"password": password}
            )

            if create and is_instructor:
                user_role = UserRole.objects.create(user=user, role=instructor_role)
                user_role.save()
                self.stdout.write(f"Created user: {email}")
            else:
                self.stdout.write(f"User '{email}' already exists")
        
        self.stdout.write(self.style.SUCCESS("Done creating users."))
