from django import forms
from app.models import Task
from app.validators.task import validate_description_contains_issue_reference


# タスクの新規作成・編集で使うフォーム
class TaskForm(forms.ModelForm):
    # モデル側の範囲指定はDB制約(CheckConstraint)のみのため、画面での一次防衛としてここで宣言する
    priority = forms.IntegerField(
        label='優先度', min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'ds-input', 'min': 1, 'max': 5}),
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ds-input'}),
            'description': forms.Textarea(attrs={'class': 'ds-input', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'ds-input'}),
            'assigned_to': forms.Select(attrs={'class': 'ds-input'}),
            'due_date': forms.DateInput(attrs={'class': 'ds-input', 'type': 'date'}),
        }

    # 画面単位の形式チェック(Validation Rulesの第1段階)。ValidationErrorはDjangoがこのフィールドに割り当てる
    def clean_description(self):
        value = self.cleaned_data['description']
        validate_description_contains_issue_reference(value)
        return value
