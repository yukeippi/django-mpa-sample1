import pytest
from app.forms.department_hierarchy import DepartmentHierarchyForm
from app.models import Company, Department, DepartmentHierarchy


# DepartmentHierarchyFormのテストクラス
@pytest.mark.django_db
class TestDepartmentHierarchyForm:

    # 親部門の選択肢は「なし」が先頭で、同じ会社の部門のうち自分以外が部門名順に並ぶこと
    def test_parent_choices_are_same_company_departments_except_self_ordered_by_name(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='B部')
        Department.objects.create(company=company, name='C部')
        Department.objects.create(company=company, name='A部')
        Department.objects.create(company=other_company, name='総務部')

        form = DepartmentHierarchyForm(instance=DepartmentHierarchy(department=department))

        assert [label for _, label in form.fields['parent_department'].choices] == [
            'なし',
            'サンプル株式会社 / A部',
            'サンプル株式会社 / C部',
        ]

    # 選択肢に無い別の会社の部門を送信すると、親部門のエラーになること
    def test_parent_in_other_company_is_invalid(self):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')
        other_company_department = Department.objects.create(
            company=Company.objects.create(name='テスト工業株式会社'), name='総務部'
        )

        form = DepartmentHierarchyForm(
            data={'parent_department': other_company_department.pk},
            instance=DepartmentHierarchy(department=department),
        )

        assert not form.is_valid()
        assert 'parent_department' in form.errors

    # 自分自身を送信すると、親部門のエラーになること
    def test_parent_self_is_invalid(self):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')

        form = DepartmentHierarchyForm(
            data={'parent_department': department.pk}, instance=DepartmentHierarchy(department=department)
        )

        assert not form.is_valid()
        assert 'parent_department' in form.errors
