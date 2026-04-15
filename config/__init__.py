from .celery import app as celery_app

# ensures Celery starts with Django
__all__ = ["celery_app"]