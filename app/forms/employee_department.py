from django import forms
from app.models import EmployeeDepartment


# 社員に所属部門を追加するフォーム
class EmployeeDepartmentForm(forms.ModelForm):

    class Meta:
        model = EmployeeDepartment
        fields = ['employee', 'department', 'is_primary']
        widgets = {
            'employee': forms.HiddenInput(),
            'department': forms.Select(attrs={'class': 'ds-input'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'ds-check'}),
        }

    # 社員はURLで決まるためdisabledにし、送信値ではなくinstanceの値を使う。
    # fieldsから外すとModelFormが社員を含む一意制約の検証を飛ばすため、fieldsには残す
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].disabled = True
