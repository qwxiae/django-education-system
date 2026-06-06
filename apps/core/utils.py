import random
from datetime import timedelta

from django.utils import timezone


def random_date_within_last_30_days():
    now = timezone.now()
    delta = timedelta(days=random.randint(0, 30), seconds=random.randint(0, 86400))
    return now - delta
