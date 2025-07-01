from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Unterweisungstyp,
    Teilnehmer,
    CheckEintrag,
    QuizFrage,
    QuizAntwort,
)

from django.contrib import admin
from .models import Unterweisungstyp, Teilnehmer, QuizFrage, QuizAntwort
from markdownx.admin import MarkdownxModelAdmin


from .models import EmailEmpfaenger
admin.site.register(EmailEmpfaenger)


@admin.register(Unterweisungstyp)
class UnterweisungstypAdmin(MarkdownxModelAdmin):
    list_display = ['name', 'unterweisung_art', 'slug']
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ['video_preview']

    def get_fields(self, request, obj=None):
        base_fields = ['name', 'slug', 'unterweisung_art']
        if obj:
            if obj.unterweisung_art == 'video':
                return base_fields + ['video', 'video_preview']
            elif obj.unterweisung_art == 'text':
                return base_fields + ['text_markdown']
        # Beim Erstellen noch keine Auswahl → beide Felder anzeigen
        return base_fields + ['video', 'video_preview', 'text_markdown']

    def video_preview(self, obj):
        if obj.video:
            return f'''
            <video width="320" height="180" controls>
                <source src="{obj.video.url}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            '''
        return "Kein Video hochgeladen."

    video_preview.allow_tags = True
    video_preview.short_description = "Vorschau Video"



@admin.register(Teilnehmer)
class TeilnehmerAdmin(admin.ModelAdmin):
    list_display = ("vorname", "nachname", "firma", "unterweisungstyp", "gueltig_bis")
    search_fields = ("vorname", "nachname", "firma")

@admin.register(CheckEintrag)
class CheckEintragAdmin(admin.ModelAdmin):
    list_display = ("teilnehmer", "aktion", "zeitpunkt")
    list_filter = ("aktion", "zeitpunkt")

class QuizAntwortInline(admin.TabularInline):
    model = QuizAntwort
    extra = 2

@admin.register(QuizFrage)
class QuizFrageAdmin(admin.ModelAdmin):
    list_display = ("frage", "unterweisungstyp")
    inlines = [QuizAntwortInline]
