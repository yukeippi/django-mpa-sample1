import pytest
from app.forms.employee_department import EmployeeDepartmentForm
from app.models import Company, Department


# EmployeeDepartmentFormのテストクラス
@pytest.mark.django_db
class TestEmployeeDepartmentForm:

    # 部門の選択肢は会社名順、同じ会社の中では部門名順に並ぶこと
    def test_department_choices_are_ordered_by_company_name_then_name(self):
        company_b = Company.objects.create(name='B株式会社')
        company_a = Company.objects.create(name='A株式会社')
        Department.objects.create(company=company_b, name='A部')
        Department.objects.create(company=company_a, name='B部')
        Department.objects.create(company=company_a, name='A部')

        form = EmployeeDepartmentForm()
        assert [(department.company.name, department.name) for department in form.fields['department'].queryset] == [
            ('A株式会社', 'A部'),
            ('A株式会社', 'B部'),
            ('B株式会社', 'A部'),
        ]
