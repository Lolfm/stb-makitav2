# management/commands/send_weekly_password.py
from django.core.management.base import BaseCommand
from unterweisungen.models import WeeklyAccess, EmailEmpfaenger
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Sendet das aktuelle wöchentliche Zugangspasswort erneut per E-Mail'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        montag = today - timedelta(days=today.weekday())

        try:
            access = WeeklyAccess.objects.get(woche=montag)
            pw = access.passwort
            recipient_list = list(EmailEmpfaenger.objects.values_list('email', flat=True))

            send_mail(
                subject="Wöchentliches Zugangspasswort [miloIT Fremdfirmenunterweisung]",
                message=f"Liebe Empfänger! \nDas neue Zugangspasswort für diese Woche lautet: {pw} \n Beste Grüße,\nDas miloIT System",
                from_email="miloIT Fremdfirmenunterweisung <noreply@miloit.at>",
                recipient_list=recipient_list
            )
            self.stdout.write(self.style.SUCCESS("Passwort erneut versendet."))
        except WeeklyAccess.DoesNotExist:
            self.stdout.write(self.style.ERROR("Für diese Woche existiert noch kein Passwort."))
