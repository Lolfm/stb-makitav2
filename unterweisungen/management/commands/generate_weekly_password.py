# management/commands/generate_weekly_password.py
from django.core.management.base import BaseCommand
from unterweisungen.models import WeeklyAccess, EmailEmpfaenger
from django.utils import timezone
import secrets
from datetime import timedelta
from django.core.mail import send_mail
from django.core.mail import EmailMessage


class Command(BaseCommand):
    help = 'Generiert ein wöchentliches Passwort für den Zugang zur Unterweisung'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        montag = today - timedelta(days=today.weekday())

        if not WeeklyAccess.objects.filter(woche=montag).exists():
            neues_pw = secrets.token_urlsafe(8)
            access = WeeklyAccess.objects.create(woche=montag, passwort=neues_pw)

            # Versenden
            recipient_list = list(EmailEmpfaenger.objects.values_list('email', flat=True))

            send_mail(
                subject="Wöchentliches Zugangspasswort [miloIT Fremdfirmenunterweisung]",
                message=f"Liebe Empfänger! \nDas neue Zugangspasswort für diese Woche lautet: {neues_pw} \n Beste Grüße,\nDas miloIT System",
                from_email="miloIT Fremdfirmenunterweisung <noreply@miloit.at>",
                recipient_list=recipient_list
            )

            self.stdout.write(self.style.SUCCESS(f"Passwort erstellt und versendet: {neues_pw}"))
        else:
            self.stdout.write("Für diese Woche existiert bereits ein Passwort.")
