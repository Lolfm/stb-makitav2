from django import forms
from .models import Teilnehmer

class TeilnehmerForm(forms.ModelForm):
    class Meta:
        model = Teilnehmer
        fields = ['vorname', 'nachname', 'firma', 'besuchsgrund', 'unterweisungstyp']
        widgets = {
            'unterschrift': forms.HiddenInput(),  # SignaturePad übernimmt das
        }


class TeilnehmerSucheForm(forms.Form):
    suchbegriff = forms.CharField(label="Name oder Firma", required=False)

