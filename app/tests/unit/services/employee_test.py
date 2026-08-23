import pytest
from app.errors.employee import DuplicateEmployeeNumberError
from app.forms.employee import EmployeeForm
from app.models import Employee
from app.services import employee as employee_service


@pytest.mark.django_db
class TestCreate:

    # 有効なフォームからUserとEmployeeが同時に作成されることを確認
    def test_creates_user_and_employee(self):
        form = EmployeeForm(data={
            'employee_number': 'E0200', 'last_name': '鈴木', 'first_name': '花子', 'password': 'pass12345',
        }, is_new=True)
        assert form.is_valid()

        employee = employee_service.create(form=form)

        assert employee.employee_number == 'E0200'
        assert employee.user.username == 'E0200'
        assert employee.user.first_name == '花子'
        assert employee.user.last_name == '鈴木'
        assert employee.user.check_password('pass12345')

    # 社員番号が重複する場合はDuplicateEmployeeNumberErrorが送出されることを確認
    def test_duplicate_employee_number_raises_error(self, sample_user):
        form = EmployeeForm(data={
            'employee_number': sample_user.employee.employee_number,
            'last_name': '鈴木', 'first_name': '花子', 'password': 'pass12345',
        }, is_new=True)
        assert form.is_valid()

        with pytest.raises(DuplicateEmployeeNumberError):
            employee_service.create(form=form)


@pytest.mark.django_db
class TestUpdate:

    # 氏名が更新され、パスワード未入力なら変更されないことを確認
    def test_updates_name_without_changing_password(self, sample_user):
        employee = sample_user.employee
        original_password_hash = sample_user.password
        form = EmployeeForm(data={
            'employee_number': employee.employee_number, 'last_name': '変更後姓', 'first_name': '変更後名',
            'password': '',
        })
        assert form.is_valid()

        employee_service.update(employee=employee, form=form)
        sample_user.refresh_from_db()

        assert sample_user.last_name == '変更後姓'
        assert sample_user.first_name == '変更後名'
        assert sample_user.password == original_password_hash

    # パスワードを入力した場合はパスワードも更新されることを確認
    def test_updates_password_when_provided(self, sample_user):
        employee = sample_user.employee
        form = EmployeeForm(data={
            'employee_number': employee.employee_number, 'last_name': '山田', 'first_name': '太郎',
            'password': 'newpass456',
        })
        assert form.is_valid()

        employee_service.update(employee=employee, form=form)
        sample_user.refresh_from_db()

        assert sample_user.check_password('newpass456')

    # 自分自身の社員番号との重複はエラーにならないことを確認(社員番号を変更しない更新)
    def test_updating_with_same_employee_number_does_not_raise_error(self, sample_user):
        employee = sample_user.employee
        form = EmployeeForm(data={
            'employee_number': employee.employee_number, 'last_name': '山田', 'first_name': '太郎', 'password': '',
        })
        assert form.is_valid()

        updated_employee = employee_service.update(employee=employee, form=form)

        assert updated_employee.employee_number == employee.employee_number

    # 他人の社員番号に変更しようとするとDuplicateEmployeeNumberErrorが送出されることを確認
    def test_duplicate_employee_number_raises_error(self, sample_user, other_user):
        employee = sample_user.employee
        form = EmployeeForm(data={
            'employee_number': other_user.employee.employee_number,
            'last_name': '山田', 'first_name': '太郎', 'password': '',
        })
        assert form.is_valid()

        with pytest.raises(DuplicateEmployeeNumberError):
            employee_service.update(employee=employee, form=form)


@pytest.mark.django_db
class TestDelete:

    # 社員(User含む)が削除されることを確認
    def test_deletes_employee_and_user(self, sample_user):
        employee = sample_user.employee
        user_id = sample_user.id

        employee_service.delete(employee=employee)

        assert Employee.objects.filter(id=employee.id).count() == 0
        from django.contrib.auth.models import User
        assert User.objects.filter(id=user_id).count() == 0
