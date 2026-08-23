import pytest
from app.forms.department import DepartmentForm
from app.models import Company


# DepartmentFormのテストクラス
@pytest.mark.django_db
class TestDepartmentForm:

    # 有効なデータでフォームが妥当と判定されることを確認
    def test_valid_data_is_valid(self):
        company = Company.objects.create(name='サンプル株式会社')
        form = DepartmentForm(data={'company': company.id, 'name': '開発部'})
        assert form.is_valid()

    # 部門名が空の場合、フォームが無効と判定されることを確認
    def test_blank_name_is_invalid(self):
        company = Company.objects.create(name='サンプル株式会社')
        form = DepartmentForm(data={'company': company.id, 'name': ''})
        assert not form.is_valid()
        assert 'name' in form.errors
