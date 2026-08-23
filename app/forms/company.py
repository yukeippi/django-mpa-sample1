from django import forms


# 会社の新規作成・編集で使うフォーム
class CompanyForm(forms.Form):
    name = forms.CharField(
        label='会社名', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'})
    )
