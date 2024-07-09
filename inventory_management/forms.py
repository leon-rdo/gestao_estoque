# forms.py
from django import forms
from .models import Product, Building

class QRCodeForm(forms.Form):
    SIZE_PRESETS = [
            ('pequeno', 'Pequeno'),
            ('medio', 'Médio'),
            ('grande', 'Grande'),
        ]
    size_preset = forms.ChoiceField(label='Tamanho', choices=SIZE_PRESETS, widget=forms.Select(attrs={'style': 'width: 300px;', 'class': 'form-select'}))


class DashboardFilterForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), required=False, label="Produto")
    building = forms.ModelChoiceField(queryset=Building.objects.all(), required=False, label="Depósito")