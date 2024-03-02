# forms.py
from django import forms
from django.core.exceptions import ValidationError

from .models import Diver


class DiverForm(forms.ModelForm):
    class Meta:
        model = Diver
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Diver.objects.filter(name__iexact=name).exists():
            raise ValidationError("This diver already exists.")
        return name
