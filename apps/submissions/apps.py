from django.apps import AppConfig


class SubmissionsConfig(AppConfig):
    name = "apps.submissions"

    def ready(self):
        import apps.submissions.signals
