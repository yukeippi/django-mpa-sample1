from django import forms
from app.models import Employee


# 社員の新規作成・編集で使うフォーム(UserとEmployeeにまたがって扱う)
class EmployeeForm(forms.ModelForm):
    # last_name/first_name/passwordはUser側の項目のため、モデルフィールドとは別に宣言する
    last_name = forms.CharField(
        label='姓', max_length=150, widget=forms.TextInput(attrs={'class': 'ds-input'})
    )
    first_name = forms.CharField(
        label='名', max_length=150, widget=forms.TextInput(attrs={'class': 'ds-input'})
    )
    password = forms.CharField(
        label='パスワード', required=False, widget=forms.PasswordInput(attrs={'class': 'ds-input'})
    )

    class Meta:
        model = Employee
        fields = ['employee_number']
        widgets = {
            'employee_number': forms.TextInput(attrs={'class': 'ds-input'}),
        }
        error_messages = {
            'employee_number': {'unique': 'この社員番号は既に使用されています。'},
        }

    # 新規作成の場合のみパスワードを必須にする(編集時は空欄なら変更しない)
    def __init__(self, *args, is_new: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_new:
            self.fields['password'].required = True
        # User側の項目はinstanceから自動で初期値が入らないため、ここで補う
        if self.instance.pk:
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['first_name'].initial = self.instance.user.first_name
