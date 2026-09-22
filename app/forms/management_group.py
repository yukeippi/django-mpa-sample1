from django import forms
from app.models import ManagementGroup
from app.permissions import rule_sets


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

    # 全社管理者フラグと部門・権限セットの整合性を検証する(複数フィールドが揃って初めて判断できる)
    def clean(self):
        cleaned_data = super().clean()
        is_admin = cleaned_data.get('is_admin')
        department = cleaned_data.get('department')
        permission_set_id = cleaned_data.get('permission_set_id')

        if is_admin and department is not None:
            raise forms.ValidationError('全社管理者グループには部門を設定できません。')
        if not is_admin and department is None:
            raise forms.ValidationError('全社管理者でない場合は部門の設定が必須です。')
        if is_admin and permission_set_id is not None:
            raise forms.ValidationError('全社管理者グループには権限セットを設定できません。')
        if not is_admin and permission_set_id is None:
            raise forms.ValidationError('全社管理者でない場合は権限セットの設定が必須です。')
        if not is_admin and permission_set_id not in rule_sets.REGISTRY:
            raise forms.ValidationError('存在しない権限セット番号です。')
        return cleaned_data
