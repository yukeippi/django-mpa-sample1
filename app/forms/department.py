from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from app.models import Company, Department


# 部門の新規作成・編集で使うフォーム
class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = ['company', 'name']
        widgets = {
            'company': forms.Select(attrs={'class': 'ds-input'}),
            'name': forms.TextInput(attrs={'class': 'ds-input'}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {'unique_together': 'この会社には同じ名前の部門が既に存在します。'},
        }

    # 会社の選択肢を会社名順に並べる(モデルにMeta.orderingを持たせないため、ここで指定する)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.order_by('name')
