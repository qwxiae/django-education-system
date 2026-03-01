from django.core.management import BaseCommand
from apps.courses.models import Category
from django.utils.text import slugify

class Command(BaseCommand):
    help = "Create default categories"

    def handle(self, *args, **kwargs):
        categories = [
            ("Mathematics", "Learn about mathematics"), 
            ("Programming", "Lear programming languages and software development"),
            ("Cybersecurity", "Cybersecurity courses: beginner to intermediate")
        ]

        for name, description in categories:
            # Defaults are necessary otherwise you would match
            # name and description creating UNIQUE error
            slug = slugify(name)
            name, created = Category.objects.get_or_create(
                # look up by slug not name
                # Mathematics and mathematics generate same slug
                slug=slug,
                defaults={"name": name, "description": description})
            if created:
                self.stdout.write(f"Created category: {name}")
            else:
                self.stdout.write(f"Category '{name}' already exists")

        self.stdout.write(self.style.SUCCESS("Done creating categories."))