from django.db import models
from django.utils import timezone
from datetime import timedelta

from markdownx.models import MarkdownxField


# models.py
class WeeklyAccess(models.Model):
    woche = models.DateField(unique=True)
    passwort = models.CharField(max_length=50, null=True, blank=True)  # ← DAS ist wichtig
    prefix = models.CharField(max_length=50, default="Makita")  # ← pro Kunde änderbar

    def __str__(self):
        return f"{self.woche} – {self.passwort}"



# Create your models here.
from django.utils.text import slugify


class Unterweisungstyp(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    UNTERWEISUNG_ARTEN = [
        ('video', 'Video'),
        ('text', 'Text'),
    ]
    unterweisung_art = models.CharField(max_length=10, choices=UNTERWEISUNG_ARTEN, default='video')

    video = models.FileField(upload_to='unterweisungsvideos/', blank=True, null=True)
    text_markdown = MarkdownxField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Teilnehmer(models.Model):
    vorname = models.CharField(max_length=100)
    nachname = models.CharField(max_length=100)
    firma = models.CharField(max_length=200)
    besuchsgrund = models.TextField()
    unterschrift_datei = models.ImageField(upload_to='signatures/', null=True, blank=True)
    unterweisungstyp = models.ForeignKey(Unterweisungstyp, on_delete=models.CASCADE)
    gueltig_bis = models.DateField(default=timezone.now() + timedelta(days=365))

    def __str__(self):
        return f"{self.vorname} {self.nachname} ({self.firma})"


class CheckEintrag(models.Model):
    teilnehmer = models.ForeignKey(Teilnehmer, on_delete=models.CASCADE)
    zeitpunkt = models.DateTimeField(auto_now_add=True)
    aktion = models.CharField(max_length=10, choices=[('ein', 'Einchecken'), ('aus', 'Auschecken')])

    def __str__(self):
        return f"{self.teilnehmer} - {self.aktion} am {self.zeitpunkt.strftime('%Y-%m-%d %H:%M')}"


class QuizFrage(models.Model):
    unterweisungstyp = models.ForeignKey(Unterweisungstyp, on_delete=models.CASCADE)
    frage = models.TextField()

class QuizAntwort(models.Model):
    frage = models.ForeignKey(QuizFrage, on_delete=models.CASCADE)
    antwort_text = models.CharField(max_length=200)
    ist_richtig = models.BooleanField(default=False)


@property
def ist_im_haus(self):
    letzter = self.checkeintrag_set.order_by('-zeitpunkt').first()
    return letzter and letzter.aktion == 'ein'
