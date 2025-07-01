# utils.py
import random
from datetime import date, timedelta
from .models import WeeklyAccess
import secrets


def get_weekly_password():
    heute = date.today()
    montag = heute - timedelta(days=heute.weekday())

    access, created = WeeklyAccess.objects.get_or_create(
        woche=montag,
        defaults={
            "prefix": "Makita",
            "passwort": None
        }
    )

    if created or not access.passwort:
        suffix = f"{random.randint(1000, 9999)}"
        access.passwort = f"{access.prefix}-{suffix}"
        access.save()

    return access.passwort
