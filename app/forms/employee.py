from django import forms


# 社員の新規作成・編集で使うフォーム(UserとEmployeeにまたがって扱う)
class EmployeeForm(forms.Form):
    employee_number = forms.CharField(
        label='社員番号', max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='姓', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='名', max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='パスワード', required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # 新規作成の場合のみパスワードを必須にする(編集時は空欄なら変更しない)
    def __init__(self, *args, is_new: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        if is_new:
            self.fields['password'].required = True
