from django import forms
from .models import Bairro, Ocorrencia

class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['bairro', 'descricao', 'status']

        # O dicionário 'widgets' injeta as classes do bootstrap direto no backend
        widgets = {
            'bairro': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control','rows': 3, 'placeholder': 'Descrição'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class BairroForm(forms.ModelForm):
    class Meta:
        model = Bairro
        fields = ['nome', 'latitude', 'longitude']
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nome do Bairro', 'list': 'lista-bairros-sugeridos',
            }),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Ex: -9.4111'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any', 'placeholder': 'Ex: -40.4986'}),
        }
