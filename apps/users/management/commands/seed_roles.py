from django.core.management.base import BaseCommand

from apps.users.models import Role


class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *args, **kwargs):
        roles = ["student", "instructor", "moderator"]

        for role_name in roles:
            role, created = Role.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f"Created role: {role_name}")
            else:
                self.stdout.write(f"Role already exists: {role_name}")

        self.stdout.write(self.style.SUCCESS("Done creating roles."))
