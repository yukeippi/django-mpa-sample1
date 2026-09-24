from django import forms
from app.models import Task


# タスクの新規作成・編集で使うフォーム
class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'ds-input'}),
            'description': forms.Textarea(attrs={'class': 'ds-input', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'ds-input'}),
            'priority': forms.NumberInput(attrs={'class': 'ds-input', 'min': 1, 'max': 5}),
            'assigned_to': forms.Select(attrs={'class': 'ds-input'}),
            'due_date': forms.DateInput(attrs={'class': 'ds-input', 'type': 'date'}),
        }


# タスク詳細画面のモーダルから、ステータスだけを変更するフォーム
class TaskStatusForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'ds-input'}),
        }
