import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from app.models import Company, Department, Employee, EmployeeDepartment


# EmployeeDepartmentモデルのテストクラス
@pytest.mark.django_db
class TestEmployeeDepartmentModel:

    # 主務として作成できること
    def test_create_as_primary(self):
        employee = _create_employee('E7001')
        department = _create_department('開発部')

        relation = EmployeeDepartment.objects.create(employee=employee, department=department, is_primary=True)

        assert relation.id is not None
        assert relation.is_primary is True

    # 同じ社員・部門の組み合わせが重複する場合はエラーになること(DB制約)
    def test_same_employee_department_pair_must_be_unique(self):
        employee = _create_employee('E7002')
        department = _create_department('開発部')
        EmployeeDepartment.objects.create(employee=employee, department=department)

        with pytest.raises(IntegrityError):
            EmployeeDepartment.objects.create(employee=employee, department=department)

    # 同じ社員に同じ部門を重複して登録しようとすると、full_clean()で文言付きのエラーになること
    def test_full_clean_rejects_duplicate_department_with_message(self):
        employee = _create_employee('E7003')
        department = _create_department('開発部')
        EmployeeDepartment.objects.create(employee=employee, department=department)

        relation = EmployeeDepartment(employee=employee, department=department)

        with pytest.raises(ValidationError) as error:
            relation.full_clean()
        assert 'この社員は既にこの部門に所属しています。' in error.value.messages

    # 1人の社員が主務を2つ持つことはできないこと(DB制約)
    def test_second_primary_for_same_employee_is_rejected_by_db(self):
        employee = _create_employee('E7004')
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'), is_primary=True)

        with pytest.raises(IntegrityError):
            EmployeeDepartment.objects.create(employee=employee, department=_create_department('営業部'), is_primary=True)

    # 既に主務がある社員に別の主務を追加しようとすると、full_clean()で文言付きのエラーになること
    def test_full_clean_rejects_second_primary_with_message(self):
        employee = _create_employee('E7005')
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'), is_primary=True)

        relation = EmployeeDepartment(employee=employee, department=_create_department('営業部'), is_primary=True)

        with pytest.raises(ValidationError) as error:
            relation.full_clean()
        assert 'この社員には既に主務の部門があります。' in error.value.messages

    # 既に主務がある社員にも、兼務の部門は追加できること
    def test_full_clean_accepts_secondary_when_primary_exists(self):
        employee = _create_employee('E7008')
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'), is_primary=True)

        relation = EmployeeDepartment(employee=employee, department=_create_department('営業部'), is_primary=False)

        relation.full_clean()

    # 兼務は1人の社員が複数持てること
    def test_employee_can_have_multiple_secondary_departments(self):
        employee = _create_employee('E7009')
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        EmployeeDepartment.objects.create(employee=employee, department=_create_department('営業部'))

        assert employee.employee_departments.count() == 2

    # 別々の社員は、それぞれ主務を1つずつ持てること
    def test_different_employees_can_each_have_primary(self):
        department = _create_department('開発部')
        EmployeeDepartment.objects.create(employee=_create_employee('E7010'), department=department, is_primary=True)

        EmployeeDepartment.objects.create(employee=_create_employee('E7011'), department=department, is_primary=True)

        assert EmployeeDepartment.objects.filter(is_primary=True).count() == 2

    # __str__が「社員 - 部門」を返すこと
    def test_str_returns_employee_and_department(self):
        employee = _create_employee('E7006')
        department = _create_department('開発部')
        relation = EmployeeDepartment.objects.create(employee=employee, department=department)

        assert str(relation) == f'{employee} - {department}'


# EmployeeDepartmentQuerySetのテストクラス
@pytest.mark.django_db
class TestEmployeeDepartmentQuerySet:

    # primary()が主務の所属のみに絞り込むこと
    def test_primary_filters_to_primary_relations(self):
        employee = _create_employee('E7007')
        primary_department = _create_department('開発部')
        secondary_department = _create_department('営業部')
        primary_relation = EmployeeDepartment.objects.create(
            employee=employee, department=primary_department, is_primary=True
        )
        EmployeeDepartment.objects.create(employee=employee, department=secondary_department)

        result = list(employee.employee_departments.primary())

        assert result == [primary_relation]


def _create_employee(employee_number):
    user = User.objects.create_user(username=employee_number, password='pass12345')
    return Employee.objects.create(user=user, employee_number=employee_number)


def _create_department(name):
    company = Company.objects.create(name=f'{name}の会社')
    return Department.objects.create(company=company, name=name)
