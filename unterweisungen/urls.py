from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.passwort_wall, name='passwort_wall'),  # ⬅ neue Route für die Passwort-Wall
    path('unterweisung/', views.unterweisung_auswahl, name='unterweisung_auswahl'),
    path('unterweisung/<slug:slug>/', views.start_unterweisung, name='unterweisung_start'),
    #path('quiz/<int:typ_id>/', views.unterweisung_quiz, name='unterweisung_quiz'),
    path("formular/<int:typ_id>/", views.unterweisung_formular, name="unterweisung_formular"),
    path('suche/', views.teilnehmer_suche, name='teilnehmer_suche'),
    path('teilnehmer/', views.teilnehmer_liste, name='teilnehmer_liste'),
    path('teilnehmer/<int:pk>/', views.teilnehmer_detail, name='teilnehmer_detail'),
    path('teilnehmer/<int:pk>/loeschen/', views.teilnehmer_loeschen, name='teilnehmer_loeschen'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("erfolg/<int:teilnehmer_id>/", views.unterweisung_erfolgreich, name="unterweisung_erfolgreich"),
    path("checkin/<int:teilnehmer_id>/", views.teilnehmer_checkin, name="teilnehmer_checkin"),
    path("login/", views.benutzer_login, name="login"),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path("teilnehmer/<int:pk>/pdf/", views.teilnehmer_pdf_export, name="teilnehmer_pdf"),
    path("teilnehmer/export/csv/", views.teilnehmer_csv_export, name="teilnehmer_csv_export"),

]
