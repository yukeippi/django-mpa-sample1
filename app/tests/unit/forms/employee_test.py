import pytest
from app.forms.employee import EmployeeForm


# EmployeeFormのテストクラス
@pytest.mark.django_db
class TestEmployeeFormCreate:

    # 有効なデータでフォームが妥当と判定されること
    def test_valid_data_is_valid(self):
        form = EmployeeForm(data={
            'employee_number': 'E0100',
            'last_name': '山田',
            'first_name': '太郎',
            'password': 'pass12345',
        }, is_new=True)
        assert form.is_valid()

    # 新規作成時はパスワードが必須であること
    def test_password_is_required_on_create(self):
        form = EmployeeForm(data={
            'employee_number': 'E0100',
            'last_name': '山田',
            'first_name': '太郎',
            'password': '',
        }, is_new=True)
        assert not form.is_valid()
        assert 'password' in form.errors


@pytest.mark.django_db
class TestEmployeeFormEdit:

    # 編集時はパスワード未入力でも妥当と判定されること
    def test_password_is_optional_on_edit(self):
        form = EmployeeForm(data={
            'employee_number': 'E0100',
            'last_name': '変更後姓',
            'first_name': '変更後名',
            'password': '',
        })
        assert form.is_valid()
