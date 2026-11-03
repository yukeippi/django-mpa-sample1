from django import forms
from app.models import Department, ManagementGroup


# 管理グループの新規作成・編集で使うフォーム
class ManagementGroupForm(forms.ModelForm):

    class Meta:
        model = ManagementGroup
        fields = ['name', 'members', 'is_admin', 'department', 'permission_set_id']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'ds-input'}),
            'members': forms.SelectMultiple(attrs={'class': 'ds-input'}),
            'is_admin': forms.CheckboxInput(attrs={'class': 'ds-check'}),
            'department': forms.Select(attrs={'class': 'ds-input'}),
            'permission_set_id': forms.NumberInput(attrs={'class': 'ds-input'}),
        }
        error_messages = {
            'name': {'unique': 'この管理グループ名は既に使用されています。'},
        }

    # 部門の選択肢を会社名・部門名順に並べる(モデルにMeta.orderingを持たせないため、ここで指定する)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.with_company().order_by('company__name', 'name')
