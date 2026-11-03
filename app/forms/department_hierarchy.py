from django import forms
from app.models import Department, DepartmentHierarchy


# 部門の親部門を変更するフォーム
class DepartmentHierarchyForm(forms.ModelForm):

    class Meta:
        model = DepartmentHierarchy
        fields = ['department', 'parent_department']
        widgets = {
            'department': forms.HiddenInput(),
            'parent_department': forms.Select(attrs={'class': 'ds-input'}),
        }

    # 部門はURLで決まるためdisabledにし、送信値ではなくinstanceの値を使う。
    # fieldsから外すとModelFormが部門を含む一意制約・clean()の検証を飛ばすため、fieldsには残す。
    # 親部門の選択肢は、同じ会社の部門のうち自分以外を部門名順に並べる(別の会社の部門はclean()でも拒否する)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].disabled = True
        department = self.instance.department
        self.fields['parent_department'].queryset = (
            Department.objects.with_company().filter(company=department.company).exclude(pk=department.pk).order_by('name')
        )
        self.fields['parent_department'].empty_label = 'なし'
