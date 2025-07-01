from django.apps import AppConfig


class UnterweisungenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'unterweisungen'

    def ready(self):
        from .utils import get_weekly_password
        from django.conf import settings

        if settings.DEBUG:
            pw = get_weekly_password()
            print(f"\n🔐 [DEBUG] Passwort-Wall Passwort dieser Woche: {pw}\n")
