from django import forms
from django.contrib.auth.models import User
from app.errors.base import DomainError
from app.models import Task
from app.validators.task import validate_description_contains_issue_reference


# タスクの新規作成・編集で使うフォーム
class TaskForm(forms.Form):
    title = forms.CharField(
        label='タイトル', max_length=200, widget=forms.TextInput(attrs={'class': 'ds-input'})
    )
    description = forms.CharField(
        label='説明', required=False, widget=forms.Textarea(attrs={'class': 'ds-input', 'rows': 4})
    )
    status = forms.ChoiceField(
        label='ステータス', choices=Task.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'ds-input'})
    )
    priority = forms.IntegerField(
        label='優先度', min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'ds-input', 'min': 1, 'max': 5}),
    )
    assigned_to = forms.ModelChoiceField(
        label='担当者', queryset=User.objects.all(), required=False,
        widget=forms.Select(attrs={'class': 'ds-input'}),
    )
    due_date = forms.DateField(
        label='期限', required=False, widget=forms.DateInput(attrs={'class': 'ds-input', 'type': 'date'})
    )

    # 画面単位の形式チェック(Validation Rulesの第1段階)。ValidatorのDomainErrorを画面表示用に変換する
    def clean_description(self):
        value = self.cleaned_data['description']
        try:
            return validate_description_contains_issue_reference(value)
        except DomainError as error:
            raise forms.ValidationError(error.message) from error
