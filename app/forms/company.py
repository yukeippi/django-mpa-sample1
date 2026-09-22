from django import forms
from app.models import Company


# 会社の新規作成・編集で使うフォーム
class CompanyForm(forms.ModelForm):

    class Meta:
        model = Company
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ds-input'}),
        }
        error_messages = {
            'name': {'unique': 'この会社名は既に使用されています。'},
        }
