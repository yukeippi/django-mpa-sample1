import pytest
from app.errors.department_hierarchy import ParentDepartmentCompanyMismatchError, SelfParentDepartmentError
from app.models import Company, Department
from app.services import department_hierarchy as department_hierarchy_service


@pytest.mark.django_db
class TestCreate:

    # 親部門を指定して部門階層が作成されることを確認
    def test_creates_hierarchy_with_parent(self):
        company = Company.objects.create(name='サンプル株式会社')
        parent = Department.objects.create(company=company, name='本社')
        child = Department.objects.create(company=company, name='営業部')

        hierarchy = department_hierarchy_service.create(department=child, parent_department=parent)

        assert hierarchy.id is not None
        assert hierarchy.parent_department == parent

    # 親部門なしで部門階層が作成されることを確認
    def test_creates_hierarchy_without_parent(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='本社')

        hierarchy = department_hierarchy_service.create(department=department, parent_department=None)

        assert hierarchy.parent_department is None

    # 親部門が別の会社に属している場合はParentDepartmentCompanyMismatchErrorが送出されることを確認
    def test_parent_in_different_company_raises_error(self):
        company_a = Company.objects.create(name='A株式会社')
        company_b = Company.objects.create(name='B株式会社')
        department = Department.objects.create(company=company_a, name='営業部')
        other_company_department = Department.objects.create(company=company_b, name='本社')

        with pytest.raises(ParentDepartmentCompanyMismatchError):
            department_hierarchy_service.create(department=department, parent_department=other_company_department)

    # 親部門に自分自身を指定した場合はSelfParentDepartmentErrorが送出されることを確認
    def test_parent_as_self_raises_error(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')

        with pytest.raises(SelfParentDepartmentError):
            department_hierarchy_service.create(department=department, parent_department=department)
