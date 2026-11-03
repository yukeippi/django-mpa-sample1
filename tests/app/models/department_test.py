import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from app.models import Company, Department, DepartmentHierarchy


# Departmentモデルのテストクラス
@pytest.mark.django_db
class TestDepartmentModel:

    # 会社と名前を指定して作成できること
    def test_create_department(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        assert department.id is not None
        assert department.company == company
        assert department.name == '開発部'

    # 同じ会社内で部門名が重複する場合はエラーになること(DB制約)
    def test_name_must_be_unique_within_company(self):
        company = Company.objects.create(name='サンプル株式会社')
        Department.objects.create(company=company, name='開発部')

        with pytest.raises(IntegrityError):
            Department.objects.create(company=company, name='開発部')

    # 別の会社であれば同じ部門名を使えること
    def test_same_name_allowed_in_different_company(self):
        company_a = Company.objects.create(name='A株式会社')
        company_b = Company.objects.create(name='B株式会社')
        Department.objects.create(company=company_a, name='開発部')

        department = Department.objects.create(company=company_b, name='開発部')

        assert department.id is not None

    # __str__が「会社名 / 部門名」を返すこと
    def test_str_returns_company_and_name(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        assert str(department) == 'サンプル株式会社 / 開発部'


# DepartmentQuerySetのテストクラス
@pytest.mark.django_db
class TestDepartmentQuerySet:

    # with_company()が全件を返すこと
    def test_with_company_returns_all_departments(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        result = list(Department.objects.with_company())

        assert result == [department]

    # with_company()がcompanyをselect_relatedし、追加クエリが発生しないこと
    def test_with_company_avoids_extra_query(self, django_assert_num_queries):
        company = Company.objects.create(name='サンプル株式会社')
        Department.objects.create(company=company, name='開発部')

        with django_assert_num_queries(1):
            department = Department.objects.with_company().first()
            str(department.company)


# 親子関係がある部門の会社変更のテストクラス
@pytest.mark.django_db
class TestDepartmentCompanyChange:

    # 親部門がある部門は、会社を変更できないこと(full_clean()で会社のエラーになる)
    def test_change_company_with_parent_fails_full_clean(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(
            department=department, parent_department=Department.objects.create(company=company, name='本社')
        )

        department.company = other_company
        with pytest.raises(ValidationError) as excinfo:
            department.full_clean()

        error = excinfo.value.error_dict['company'][0]
        assert error.code == 'department_company_change_with_hierarchy'
        assert error.messages == ['親部門・子部門がある部門は会社を変更できません。先に親子関係を外してください。']

    # 子部門がある部門は、会社を変更できないこと
    def test_change_company_with_child_fails_full_clean(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='本社')
        DepartmentHierarchy.objects.create(
            department=Department.objects.create(company=company, name='営業部'), parent_department=department
        )

        department.company = other_company
        with pytest.raises(ValidationError) as excinfo:
            department.full_clean()

        assert excinfo.value.error_dict['company'][0].code == 'department_company_change_with_hierarchy'

    # 親部門も子部門も無い部門は、会社を変更できること
    def test_change_company_without_hierarchy_passes_full_clean(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='営業部')

        department.company = other_company
        department.full_clean()

    # 親部門が「なし」の階層レコードしか無い部門は、親部門も子部門も無いため会社を変更できること
    def test_change_company_with_hierarchy_without_parent_passes_full_clean(self):
        company = Company.objects.create(name='サンプル株式会社')
        other_company = Company.objects.create(name='テスト工業株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(department=department, parent_department=None)

        department.company = other_company
        department.full_clean()

    # 会社を変えずに部門名だけを変更する場合は、親部門があっても変更できること
    def test_change_name_only_with_parent_passes_full_clean(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(
            department=department, parent_department=Department.objects.create(company=company, name='本社')
        )

        department.name = '第一営業部'
        department.full_clean()
