import pytest
from django.db import IntegrityError
from app.models import Company, Department, DepartmentHierarchy


# DepartmentHierarchyモデルのテストクラス
@pytest.mark.django_db
class TestDepartmentHierarchyModel:

    # 親部門を指定して作成できること
    def test_create_with_parent(self):
        company = Company.objects.create(name='サンプル株式会社')
        parent = Department.objects.create(company=company, name='本社')
        child = Department.objects.create(company=company, name='営業部')

        hierarchy = DepartmentHierarchy.objects.create(department=child, parent_department=parent)

        assert hierarchy.id is not None
        assert hierarchy.department == child
        assert hierarchy.parent_department == parent

    # 親部門なし(最上位の部門)で作成できること
    def test_create_without_parent(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='本社')

        hierarchy = DepartmentHierarchy.objects.create(department=department)

        assert hierarchy.id is not None
        assert hierarchy.parent_department is None

    # 同じ部門で2件目のレコードを作成しようとするとエラーになること(1部門につき1レコード。OneToOneField由来のDB制約)
    def test_department_must_be_unique(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(department=department)

        with pytest.raises(IntegrityError):
            DepartmentHierarchy.objects.create(department=department)

    # 親部門に自分自身を指定した場合はエラーになること(DB制約)
    def test_parent_cannot_be_self(self):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')

        with pytest.raises(IntegrityError):
            DepartmentHierarchy.objects.create(department=department, parent_department=department)

    # __str__が「部門 (親: 親部門)」の形式を返すこと
    def test_str_includes_department_and_parent(self):
        company = Company.objects.create(name='サンプル株式会社')
        parent = Department.objects.create(company=company, name='本社')
        child = Department.objects.create(company=company, name='営業部')
        hierarchy = DepartmentHierarchy.objects.create(department=child, parent_department=parent)

        assert str(hierarchy) == f'{child} (親: {parent})'
