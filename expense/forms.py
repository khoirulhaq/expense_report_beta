from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['tanggal', 'kategori', 'nominal', 'catatan', 'prioritas', 'dompet']
        widgets = {
            'tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'kategori': forms.Select(attrs={'class': 'form-select'}),
            'nominal': forms.NumberInput(attrs={'class': 'form-control'}),
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prioritas': forms.Select(attrs={'class': 'form-select'}),
            'dompet': forms.Select(attrs={'class': 'form-select'}),
        }
