import pytest
from django.contrib.auth.models import User
from django.test import Client
from app.models import Company, Department, EmployeeDepartment, ManagementGroup


# admin_client(pytest-djangoのis_staffユーザー)を、全社管理者グループ(ManagementGroup.is_admin)にも所属させる
@pytest.fixture(autouse=True)
def _grant_group_admin(admin_user):
    group = ManagementGroup.objects.create(name='test-admin-group', is_admin=True)
    group.members.add(admin_user)


@pytest.mark.django_db
class TestEmployeeDepartmentNewView:

    # 部門を主務として追加でき、社員詳細画面にリダイレクトされること
    def test_post_adds_primary_department_and_redirects_to_employee(self, admin_client, sample_user):
        employee = sample_user.employee
        department = _create_department('開発部')

        response = admin_client.post(f'/employees/{employee.pk}/departments/new/', {
            'department': department.pk, 'is_primary': 'on',
        })

        assert response.status_code == 302
        assert response.url == f'/employees/{employee.pk}/'
        relation = EmployeeDepartment.objects.get(employee=employee)
        assert relation.department == department
        assert relation.is_primary is True

    # 部門を兼務として追加できること
    def test_post_adds_secondary_department(self, admin_client, sample_user):
        employee = sample_user.employee
        department = _create_department('開発部')

        admin_client.post(f'/employees/{employee.pk}/departments/new/', {'department': department.pk})

        relation = EmployeeDepartment.objects.get(employee=employee)
        assert relation.is_primary is False

    # 追加すると「所属部門を追加しました。」が表示されること
    def test_post_shows_success_message(self, admin_client, sample_user):
        employee = sample_user.employee
        department = _create_department('開発部')

        response = admin_client.post(
            f'/employees/{employee.pk}/departments/new/', {'department': department.pk}, follow=True
        )

        assert '所属部門を追加しました。' in [str(message) for message in response.context['messages']]

    # 既に所属している部門は追加できず、エラーが表示され、所属は増えないこと
    def test_post_duplicate_department_is_rejected(self, admin_client, sample_user):
        employee = sample_user.employee
        department = _create_department('開発部')
        EmployeeDepartment.objects.create(employee=employee, department=department)

        response = admin_client.post(f'/employees/{employee.pk}/departments/new/', {'department': department.pk})

        assert response.status_code == 200
        assert 'この社員は既にこの部門に所属しています。' in response.content.decode()
        assert EmployeeDepartment.objects.filter(employee=employee).count() == 1

    # 既に主務がある社員に別の部門を主務として追加できず、エラーが表示され、所属は増えないこと
    def test_post_second_primary_is_rejected(self, admin_client, sample_user):
        employee = sample_user.employee
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'), is_primary=True)
        other_department = _create_department('営業部')

        response = admin_client.post(f'/employees/{employee.pk}/departments/new/', {
            'department': other_department.pk, 'is_primary': 'on',
        })

        assert response.status_code == 200
        assert 'この社員には既に主務の部門があります。' in response.content.decode()
        assert EmployeeDepartment.objects.filter(employee=employee).count() == 1

    # 既に主務がある社員にも、別の部門を兼務として追加できること
    def test_post_secondary_when_primary_exists_succeeds(self, admin_client, sample_user):
        employee = sample_user.employee
        EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'), is_primary=True)
        other_department = _create_department('営業部')

        admin_client.post(f'/employees/{employee.pk}/departments/new/', {'department': other_department.pk})

        assert EmployeeDepartment.objects.filter(employee=employee).count() == 2

    # 全社管理者は追加フォームを表示できること
    def test_get_by_admin_displays_form(self, admin_client, sample_user):
        response = admin_client.get(f'/employees/{sample_user.employee.pk}/departments/new/')

        assert response.status_code == 200

    # 全社管理者でないユーザーは追加フォームを表示できないこと(403)
    def test_get_by_non_admin_returns_403(self, auth_client, other_user):
        response = auth_client.get(f'/employees/{other_user.employee.pk}/departments/new/')

        assert response.status_code == 403

    # 全社管理者でないユーザーは追加できず(403)、所属は変わらないこと
    def test_post_by_non_admin_returns_403_and_does_not_add(self, auth_client, other_user):
        department = _create_department('開発部')

        response = auth_client.post(
            f'/employees/{other_user.employee.pk}/departments/new/', {'department': department.pk}
        )

        assert response.status_code == 403
        assert not EmployeeDepartment.objects.exists()

    # is_staffでも全社管理者グループのメンバーでなければ追加できないこと(403)
    def test_post_by_staff_without_admin_group_returns_403(self, sample_user, other_user):
        staff_user = User.objects.create_user(username='staff', password='pass12345', is_staff=True)
        department = _create_department('開発部')
        client = _login(staff_user)

        response = client.post(f'/employees/{other_user.employee.pk}/departments/new/', {'department': department.pk})

        assert response.status_code == 403
        assert not EmployeeDepartment.objects.exists()

    # 存在しない社員の場合は404になること
    def test_nonexistent_employee_returns_404(self, admin_client):
        response = admin_client.get('/employees/9999/departments/new/')

        assert response.status_code == 404

    # 未ログインの場合はログインページにリダイレクトされること
    def test_requires_login(self, client, sample_user):
        response = client.get(f'/employees/{sample_user.employee.pk}/departments/new/')

        assert response.status_code == 302
        assert response.url.startswith('/login/')


@pytest.mark.django_db
class TestEmployeeDepartmentDeleteView:

    # 所属を外すと、社員詳細画面にリダイレクトされること
    def test_post_removes_department_and_redirects_to_employee(self, admin_client, sample_user):
        employee = sample_user.employee
        relation = EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        response = admin_client.post(f'/employees/{employee.pk}/departments/{relation.pk}/delete/')

        assert response.status_code == 302
        assert response.url == f'/employees/{employee.pk}/'
        assert not EmployeeDepartment.objects.filter(pk=relation.pk).exists()

    # 外すと「所属部門を外しました。」が表示されること
    def test_post_shows_success_message(self, admin_client, sample_user):
        employee = sample_user.employee
        relation = EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        response = admin_client.post(f'/employees/{employee.pk}/departments/{relation.pk}/delete/', follow=True)

        assert '所属部門を外しました。' in [str(message) for message in response.context['messages']]

    # 主務も外せ、外した後は主務なしになること
    def test_post_removes_primary_department(self, admin_client, sample_user):
        employee = sample_user.employee
        relation = EmployeeDepartment.objects.create(
            employee=employee, department=_create_department('開発部'), is_primary=True
        )

        admin_client.post(f'/employees/{employee.pk}/departments/{relation.pk}/delete/')

        assert not EmployeeDepartment.objects.filter(employee=employee, is_primary=True).exists()

    # GETでは所属は外れないこと
    def test_get_does_not_remove_department(self, admin_client, sample_user):
        employee = sample_user.employee
        relation = EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        admin_client.get(f'/employees/{employee.pk}/departments/{relation.pk}/delete/')

        assert EmployeeDepartment.objects.filter(pk=relation.pk).exists()

    # 全社管理者でないユーザーは外せず(403)、所属は変わらないこと
    def test_post_by_non_admin_returns_403_and_does_not_remove(self, auth_client, other_user):
        employee = other_user.employee
        relation = EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        response = auth_client.post(f'/employees/{employee.pk}/departments/{relation.pk}/delete/')

        assert response.status_code == 403
        assert EmployeeDepartment.objects.filter(pk=relation.pk).exists()

    # 存在しない所属の場合は404になること
    def test_nonexistent_relation_returns_404(self, admin_client, sample_user):
        response = admin_client.post(f'/employees/{sample_user.employee.pk}/departments/9999/delete/')

        assert response.status_code == 404

    # URLの社員と所属の社員が違う場合は404になり、所属は変わらないこと(存在しない所属と同じ扱い)
    def test_relation_of_other_employee_returns_404_and_does_not_remove(self, admin_client, sample_user, other_user):
        relation = EmployeeDepartment.objects.create(
            employee=other_user.employee, department=_create_department('開発部')
        )

        response = admin_client.post(f'/employees/{sample_user.employee.pk}/departments/{relation.pk}/delete/')

        assert response.status_code == 404
        assert EmployeeDepartment.objects.filter(pk=relation.pk).exists()

    # 未ログインの場合はログインページにリダイレクトされ、所属は変わらないこと
    def test_requires_login(self, client, sample_user):
        employee = sample_user.employee
        relation = EmployeeDepartment.objects.create(employee=employee, department=_create_department('開発部'))

        response = client.post(f'/employees/{employee.pk}/departments/{relation.pk}/delete/')

        assert response.status_code == 302
        assert response.url.startswith('/login/')
        assert EmployeeDepartment.objects.filter(pk=relation.pk).exists()


def _create_department(name):
    company = Company.objects.create(name=f'{name}の会社')
    return Department.objects.create(company=company, name=name)


def _login(user):
    client = Client()
    client.force_login(user)
    return client
