from django import forms
from django.contrib.auth.models import User
from app.models import Department


# 管理グループの新規作成・編集で使うフォーム
class ManagementGroupForm(forms.Form):
    name = forms.CharField(
        label='管理グループ名', max_length=100, widget=forms.TextInput(attrs={'class': 'ds-input'})
    )
    members = forms.ModelMultipleChoiceField(
        label='メンバー', queryset=User.objects.all(), required=False,
        widget=forms.SelectMultiple(attrs={'class': 'ds-input'}),
    )
    is_admin = forms.BooleanField(
        label='全社管理者', required=False, widget=forms.CheckboxInput(attrs={'class': 'ds-check'})
    )
    department = forms.ModelChoiceField(
        label='割当部門', queryset=Department.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'ds-input'}),
    )
    permission_set_id = forms.IntegerField(
        label='権限セット番号', required=False, widget=forms.NumberInput(attrs={'class': 'ds-input'})
    )
