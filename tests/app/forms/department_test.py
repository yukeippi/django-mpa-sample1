import pytest
from app.forms.department import DepartmentForm
from app.models import Company


# DepartmentFormのテストクラス
@pytest.mark.django_db
class TestDepartmentForm:

    # 有効なデータでフォームが妥当と判定されること
    def test_valid_data_is_valid(self):
        company = Company.objects.create(name='サンプル株式会社')
        form = DepartmentForm(data={'company': company.id, 'name': '開発部'})
        assert form.is_valid()

    # 部門名が空の場合、フォームが無効と判定されること
    def test_blank_name_is_invalid(self):
        company = Company.objects.create(name='サンプル株式会社')
        form = DepartmentForm(data={'company': company.id, 'name': ''})
        assert not form.is_valid()
        assert 'name' in form.errors

    # 会社の選択肢は会社名順に並ぶこと
    def test_company_choices_are_ordered_by_name(self):
        for name in ['C株式会社', 'A株式会社', 'B株式会社']:
            Company.objects.create(name=name)

        form = DepartmentForm()
        assert [company.name for company in form.fields['company'].queryset] == ['A株式会社', 'B株式会社', 'C株式会社']
