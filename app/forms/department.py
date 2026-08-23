from django import forms
from app.models import Company


# 部門の新規作成・編集で使うフォーム
class DepartmentForm(forms.Form):
    company = forms.ModelChoiceField(
        label='会社', queryset=Company.objects.all(), widget=forms.Select(attrs={'class': 'form-select'})
    )
    name = forms.CharField(
        label='部門名', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
