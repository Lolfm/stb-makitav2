# management/commands/generate_weekly_password.py
from django.core.management.base import BaseCommand
from unterweisungen.models import WeeklyAccess
from django.utils import timezone
import secrets
from datetime import timedelta
from django.core.mail import send_mail


class Command(BaseCommand):
    help = 'Generiert ein wöchentliches Passwort für den Zugang zur Unterweisung'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        montag = today - timedelta(days=today.weekday())

        if not WeeklyAccess.objects.filter(woche=montag).exists():
            neues_pw = secrets.token_urlsafe(8)
            access = WeeklyAccess.objects.create(woche=montag, passwort=neues_pw)

            # Versenden
            send_mail(
                subject="Wöchentliches Zugangspasswort",
                message=f"Das neue Zugangspasswort lautet: {neues_pw}",
                from_email="system@deinefirma.at",
                recipient_list=["empfang@deinefirma.at", "chef@firma.at"]
            )
            self.stdout.write(self.style.SUCCESS(f"Passwort erstellt und versendet: {neues_pw}"))
        else:
            self.stdout.write("Für diese Woche existiert bereits ein Passwort.")
