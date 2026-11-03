import pytest
from app.forms.department import DepartmentForm
from app.models import Company, Department, DepartmentHierarchy


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

    # 親部門がある部門の会社を変更すると、会社の欄にエラーが表示されること
    def test_change_company_with_parent_shows_error_on_company(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(
            department=department, parent_department=Department.objects.create(company=company, name='本社')
        )

        form = DepartmentForm(data={'company': other_company.id, 'name': '営業部'}, instance=department)

        assert not form.is_valid()
        assert form.errors['company'] == ['親部門・子部門がある部門は会社を変更できません。先に親子関係を外してください。']
