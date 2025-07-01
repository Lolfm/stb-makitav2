from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from unterweisungen.models import Teilnehmer, CheckEintrag

class Command(BaseCommand):
    help = "Erstellt die Gruppen Superadmin, Admin und Empfang mit passenden Berechtigungen"

    def handle(self, *args, **kwargs):
        # Gruppe: Superadmin – bekommt alle Rechte (normalerweise via is_superuser)
        superadmin, _ = Group.objects.get_or_create(name="Superadmin")

        # Gruppe: Admin – bekommt volle Rechte auf Teilnehmer + CheckEintrag
        admin, _ = Group.objects.get_or_create(name="Admin")
        admin_permissions = Permission.objects.filter(
            content_type__model__in=["teilnehmer", "checkeintrag"]
        )
        admin.permissions.set(admin_permissions)

        # Gruppe: Empfang – darf nur Teilnehmer sehen & Checkins machen
        empfang, _ = Group.objects.get_or_create(name="Empfang")
        empfang_permissions = Permission.objects.filter(
            codename__in=[
                "view_teilnehmer",
                "view_checkeintrag",
                "add_checkeintrag",
            ]
        )
        empfang.permissions.set(empfang_permissions)

        self.stdout.write(self.style.SUCCESS("Gruppen und Berechtigungen erfolgreich erstellt."))
