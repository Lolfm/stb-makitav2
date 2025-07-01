import markdown
from django.shortcuts import render, redirect
from .models import QuizFrage, QuizAntwort, Unterweisungstyp, WeeklyAccess
from .forms import TeilnehmerForm
from datetime import date, timedelta
import base64
import uuid
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Teilnehmer, CheckEintrag
from .forms import TeilnehmerSucheForm
from django.utils.timezone import now

from .models import Unterweisungstyp

from django.contrib import messages

from django.contrib import messages
import markdown


from django.contrib.auth.decorators import login_required, user_passes_test

def in_checkin_gruppe(user):
    return user.groups.filter(name__in=["Superadmin", "Admin"]).exists()


def start_unterweisung(request, slug):
    unterweisung = get_object_or_404(Unterweisungstyp, slug=slug)
    fragen = QuizFrage.objects.filter(unterweisungstyp=unterweisung)

    if unterweisung.unterweisung_art == 'text':
        unterweisung.text_html = markdown.markdown(unterweisung.text_markdown or "", extensions=["extra", "sane_lists", "nl2br"])


    if request.method == "POST":
        richtige_antworten = 0

        for frage in fragen:
            selected_id = request.POST.get(f"frage_{frage.id}")
            if selected_id:
                antwort = QuizAntwort.objects.filter(id=selected_id, frage=frage, ist_richtig=True).first()
                if antwort:
                    richtige_antworten += 1

        if richtige_antworten >= 2:
            request.session["unterweisung_typ_id"] = unterweisung.id
            return redirect("unterweisung_formular", unterweisung.id)
        else:
            messages.error(request, "Du musst mindestens 2 Fragen richtig beantworten. Bitte versuche es erneut.")

    return render(request, 'unterweisungen/unterweisung_text.html' if unterweisung.unterweisung_art == "text" else 'unterweisungen/unterweisung_video.html', {
        "unterweisung": unterweisung,
        "fragen": fragen
    })



def unterweisung_auswahl(request):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    unterweisungstypen = Unterweisungstyp.objects.all()
    return render(request, "unterweisungen/unterweisung_auswahl.html", {
        "unterweisungstypen": unterweisungstypen
    })


def unterweisung_starten(request, slug):
    typ = get_object_or_404(Unterweisungstyp, slug=slug)

    # Markdown vorbereiten, falls Textversion
    text_html = ""
    if typ.unterweisung_art == "text" and typ.text_unterweisung:
        text_html = markdown.markdown(typ.text_unterweisung)

    return render(request, 'unterweisungen/unterweisung_start.html', {
        'typ': typ,
        'text_html': text_html
    })


from django.contrib import messages
'''
def unterweisung_quiz(request, typ_id):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    unterweisungstyp = get_object_or_404(Unterweisungstyp, id=typ_id)
    fragen = QuizFrage.objects.filter(unterweisungstyp=unterweisungstyp)

    if request.method == "POST":
        richtige_antworten = 0

        for frage in fragen:
            selected_id = request.POST.get(f"frage_{frage.id}")
            if selected_id:
                antwort = QuizAntwort.objects.filter(id=selected_id, frage=frage, ist_richtig=True).first()
                if antwort:
                    richtige_antworten += 1

        if richtige_antworten >= 2:  # oder len(fragen) falls du flexibel sein willst
            request.session["unterweisung_typ_id"] = unterweisungstyp.id
            return redirect("unterweisung_formular", typ_id)  # oder deine Zielview

        messages.error(request, "Du musst mindestens 2 Fragen richtig beantworten. Bitte versuche es erneut.")
'''
#    return render(request, "unterweisungen/quiz.html", {
#        "unterweisungstyp": unterweisungstyp,
#        "fragen": fragen,
#    })



def unterweisung_formular(request, typ_id):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    unterweisungstyp = get_object_or_404(Unterweisungstyp, id=typ_id)
    if request.method == "POST":
        form = TeilnehmerForm(request.POST, request.FILES)
        if form.is_valid():
            teilnehmer = form.save(commit=False)
            teilnehmer.unterweisungstyp = unterweisungstyp
            teilnehmer.gueltig_bis = date.today() + timedelta(days=365)

            # Base64 Unterschrift extrahieren und als Datei speichern
            base64_data = request.POST.get('unterschrift')
            if base64_data and base64_data.startswith('data:image'):
                format, imgstr = base64_data.split(';base64,')
                ext = format.split('/')[-1]
                file_name = f"{uuid.uuid4()}.{ext}"
                data = ContentFile(base64.b64decode(imgstr), name=file_name)

                # Optional: neues Feld 'unterschrift_datei' verwenden
                teilnehmer.unterschrift_datei = data

                print(file_name)

            teilnehmer.save()
            return redirect("unterweisung_erfolgreich", teilnehmer.id)
    else:
        form = TeilnehmerForm()
    return render(request, "unterweisungen/formular.html", {
        "form": form,
        "unterweisungstyp": unterweisungstyp,
    })

def unterweisung_erfolgreich(request, teilnehmer_id):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    teilnehmer = get_object_or_404(Teilnehmer, id=teilnehmer_id)
    return render(request, "unterweisungen/erfolg.html", {"teilnehmer": teilnehmer})


@login_required
def teilnehmer_suche(request):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    form = TeilnehmerSucheForm(request.GET or None)
    teilnehmer_liste = []

    if form.is_valid():
        suchbegriff = form.cleaned_data.get("suchbegriff")
        if suchbegriff:
            teilnehmer_liste = Teilnehmer.objects.filter(
                Q(vorname__icontains=suchbegriff) |
                Q(nachname__icontains=suchbegriff) |
                Q(firma__icontains=suchbegriff)
            )

        # Status & Gültigkeit berechnen
        for teilnehmer in teilnehmer_liste:
            letzter_check = CheckEintrag.objects.filter(teilnehmer=teilnehmer).order_by('-zeitpunkt').first()
            teilnehmer.status = "Nicht im Haus"
            if letzter_check and letzter_check.aktion == 'ein':
                teilnehmer.status = "Im Haus"
            teilnehmer.ist_gueltig = teilnehmer.gueltig_bis >= now().date()

    return render(request, 'unterweisungen/teilnehmer_suche.html', {
        "form": form,
        "teilnehmer_liste": teilnehmer_liste,
    })

from .models import Teilnehmer, CheckEintrag
from django.utils import timezone

@login_required
def teilnehmer_checkin(request, teilnehmer_id):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    teilnehmer = get_object_or_404(Teilnehmer, id=teilnehmer_id)

    # prüfen ob Teilnehmer schon heute eingecheckt ist (optional)
    letzter_eintrag = CheckEintrag.objects.filter(teilnehmer=teilnehmer).order_by('-zeitpunkt').first()
    if letzter_eintrag and letzter_eintrag.aktion == 'ein':
        messages.info(request, f"{teilnehmer.vorname} ist bereits eingecheckt.")
    else:
        CheckEintrag.objects.create(
            teilnehmer=teilnehmer,
            aktion='ein',
            zeitpunkt=timezone.now()
        )
        messages.success(request, f"{teilnehmer.vorname} wurde erfolgreich eingecheckt.")

    return redirect("unterweisung_erfolgreich", teilnehmer.id)



from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Teilnehmer, CheckEintrag
from .forms import TeilnehmerSucheForm
from datetime import date
from django.utils.timezone import now

@login_required
def teilnehmer_liste(request):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    form = TeilnehmerSucheForm(request.GET or None)
    heute = date.today()
    dashboard_filter = request.GET.get("filter")

    teilnehmer_liste = Teilnehmer.objects.all()

    # Filter Gültigkeit
    if dashboard_filter == "gueltig":
        teilnehmer_liste = teilnehmer_liste.filter(gueltig_bis__gte=heute)
    elif dashboard_filter == "abgelaufen":
        teilnehmer_liste = teilnehmer_liste.filter(gueltig_bis__lt=heute)

    # Status "im Haus" / "nicht im Haus"
    if dashboard_filter in ["imhaus", "nichthaus"]:
        ids = []
        for t in teilnehmer_liste:
            letzter = CheckEintrag.objects.filter(teilnehmer=t).order_by('-zeitpunkt').first()
            ist_im_haus = letzter and letzter.aktion == "ein"
            if dashboard_filter == "imhaus" and ist_im_haus:
                ids.append(t.id)
            elif dashboard_filter == "nichthaus" and not ist_im_haus:
                ids.append(t.id)
        teilnehmer_liste = teilnehmer_liste.filter(id__in=ids)

    # Suche
    if form.is_valid():
        suchbegriff = form.cleaned_data.get("suchbegriff")
        if suchbegriff:
            teilnehmer_liste = teilnehmer_liste.filter(
                Q(vorname__icontains=suchbegriff) |
                Q(nachname__icontains=suchbegriff) |
                Q(firma__icontains=suchbegriff)
            )

    # Status & Gültigkeit berechnen (für Anzeige im Template)
    for t in teilnehmer_liste:
        letzter = CheckEintrag.objects.filter(teilnehmer=t).order_by('-zeitpunkt').first()
        t.status = "Im Haus" if letzter and letzter.aktion == "ein" else "Nicht im Haus"
        t.ist_gueltig = t.gueltig_bis >= heute

    return render(request, 'unterweisungen/teilnehmer_liste.html', {
        "form": form,
        "teilnehmer_liste": teilnehmer_liste,
    })


@login_required
def teilnehmer_detail(request, pk):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    teilnehmer = get_object_or_404(Teilnehmer, pk=pk)
    check_history = CheckEintrag.objects.filter(teilnehmer=teilnehmer).order_by('-zeitpunkt')

    # Check-In / Out Logik
    if request.method == "POST":
        if 'checkin' in request.POST:
            CheckEintrag.objects.create(teilnehmer=teilnehmer, aktion='ein')
        elif 'checkout' in request.POST:
            CheckEintrag.objects.create(teilnehmer=teilnehmer, aktion='aus')
        return redirect('teilnehmer_detail', pk=pk)

    # Status berechnen
    letzter_check = CheckEintrag.objects.filter(teilnehmer=teilnehmer).order_by('-zeitpunkt').first()
    status = "Nicht im Haus"
    if letzter_check and letzter_check.aktion == 'ein':
        status = "Im Haus"

    ist_gueltig = teilnehmer.gueltig_bis >= now().date()

    return render(request, 'unterweisungen/teilnehmer_detail.html', {
        "teilnehmer": teilnehmer,
        "status": status,
        "ist_gueltig": ist_gueltig,
        "check_history": check_history,
    })


import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from io import BytesIO
from .models import Teilnehmer

def teilnehmer_pdf_export(request, pk):
    teilnehmer = get_object_or_404(Teilnehmer, pk=pk)

    unterschrift_pfad = ""
    if teilnehmer.unterschrift_datei:
        unterschrift_pfad = os.path.join(settings.MEDIA_ROOT, teilnehmer.unterschrift_datei.name)

    template = get_template("unterweisungen/teilnehmer_pdf.html")
    html = template.render({
        "teilnehmer": teilnehmer,
        "unterschrift_pfad": unterschrift_pfad
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="teilnehmer_{teilnehmer.id}.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), dest=response, encoding='UTF-8')

    if pisa_status.err:
        return HttpResponse('Fehler beim PDF-Export', status=500)
    return response


from django.views.decorators.http import require_POST

@require_POST
def teilnehmer_loeschen(request, pk):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    teilnehmer = get_object_or_404(Teilnehmer, pk=pk)
    teilnehmer.delete()
    messages.success(request, "Teilnehmer wurde gelöscht.")
    return redirect('teilnehmer_liste')


@login_required
@user_passes_test(in_checkin_gruppe)
def dashboard(request):
    if not request.session.get('zugang_erlaubt'):
        return redirect('passwort_wall')

    heute = date.today()

    alle_teilnehmer = Teilnehmer.objects.all()
    gueltige = alle_teilnehmer.filter(gueltig_bis__gte=heute).count()
    abgelaufen = alle_teilnehmer.filter(gueltig_bis__lt=heute).count()
    gesamt = alle_teilnehmer.count()

    # Letzter Check-Eintrag auswerten
    im_haus_ids = []
    nicht_im_haus_ids = []

    for t in alle_teilnehmer:
        letzter = CheckEintrag.objects.filter(teilnehmer=t).order_by('-zeitpunkt').first()
        if letzter and letzter.aktion == 'ein':
            im_haus_ids.append(t.id)
        else:
            nicht_im_haus_ids.append(t.id)

    im_haus = len(im_haus_ids)
    nicht_im_haus = len(nicht_im_haus_ids)

    heute_checkins = CheckEintrag.objects.filter(
        aktion='ein', zeitpunkt__date=heute
    ).count()

    return render(request, 'unterweisungen/dashboard.html', {
        "gesamt": gesamt,
        "gueltige": gueltige,
        "abgelaufen": abgelaufen,
        "im_haus": im_haus,
        "nicht_im_haus": nicht_im_haus,
        "heute_checkins": heute_checkins,
    })


def passwort_wall(request):
    error = False

    if request.method == "POST":
        eingegeben = request.POST.get("passwort", "")
        montag = timezone.now().date() - timedelta(days=timezone.now().weekday())
        try:
            aktuelles = WeeklyAccess.objects.get(woche=montag)
            if eingegeben == aktuelles.passwort:
                request.session['zugang_erlaubt'] = True
                return redirect('unterweisung_auswahl')
            else:
                error = True
        except WeeklyAccess.DoesNotExist:
            error = True

    return render(request, "unterweisungen/passwort_wall.html", {"error": error})


from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

def benutzer_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Weiterleitung je nach Gruppe
            if user.groups.filter(name="Empfang").exists():
                return redirect("unterweisung_auswahl")
            else:
                return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "unterweisungen/login.html", {"form": form})

import csv
from django.http import HttpResponse

def teilnehmer_csv_export(request):
    if not request.user.is_authenticated or not request.user.groups.filter(name__in=["Admin", "Superadmin"]).exists():
        return HttpResponse(status=403)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="teilnehmer_liste.csv"'

    writer = csv.writer(response)
    writer.writerow(['Vorname', 'Nachname', 'Firma', 'Gültig bis', 'Unterweisung'])

    for t in Teilnehmer.objects.all():
        writer.writerow([t.vorname, t.nachname, t.firma, t.gueltig_bis.strftime("%d.%m.%Y"), t.unterweisungstyp.name])

    return response
