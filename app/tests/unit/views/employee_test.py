import pytest
from django.contrib.auth.models import User
from app.models import Company, Department, Employee, EmployeeDepartment, ManagementGroup

DEPARTMENT_VIEWER_ALL = 1


# admin_client(pytest-djangoのis_staffユーザー)を、新しいアクセス制御(ManagementGroup.is_admin)の
# 全社管理者グループにも所属させる(is_staffと新しいアクセス制御は別の仕組みのため)
@pytest.fixture(autouse=True)
def _grant_group_admin(admin_user):
    group = ManagementGroup.objects.create(name='test-admin-group', is_admin=True)
    group.members.add(admin_user)


@pytest.mark.django_db
class TestEmployeeIndexView:

    # 未ログインの場合、ログインページにリダイレクトされることを確認
    def test_index_requires_login(self, client):
        response = client.get('/employees/')
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # Employeeを対象とするルールを持たない権限セットのユーザーには一覧が0件になることを確認
    def test_index_by_user_without_permission_is_empty(self, sample_user, other_user, auth_client):
        _grant(sample_user, DEPARTMENT_VIEWER_ALL)

        response = auth_client.get('/employees/')
        assert response.status_code == 200
        assert len(response.context['employees']) == 0

    # 管理者は一覧を取得できることを確認
    def test_index_by_admin_succeeds(self, admin_client, sample_user):
        response = admin_client.get('/employees/')
        assert response.status_code == 200
        assert sample_user.employee in response.context['employees']


@pytest.mark.django_db
class TestEmployeeShowView:

    # 閲覧権限が無いユーザーがアクセスすると403が返ることを確認
    def test_show_by_user_without_permission_returns_403(self, sample_user, other_user, auth_client):
        _grant(sample_user, DEPARTMENT_VIEWER_ALL)

        response = auth_client.get(f'/employees/{other_user.employee.id}/')
        assert response.status_code == 403

    # 管理者は詳細を取得できることを確認
    def test_show_by_admin_succeeds(self, admin_client, sample_user):
        response = admin_client.get(f'/employees/{sample_user.employee.id}/')
        assert response.status_code == 200
        assert response.context['employee'] == sample_user.employee

    # 存在しない社員の場合404が返ることを確認
    def test_show_nonexistent_employee_returns_404(self, admin_client):
        response = admin_client.get('/employees/9999/')
        assert response.status_code == 404


@pytest.mark.django_db
class TestEmployeeCreateView:

    # 作成権限が無いユーザーがアクセスすると403が返ることを確認
    def test_new_by_user_without_create_permission_returns_403(self, sample_user, auth_client):
        _grant(sample_user, DEPARTMENT_VIEWER_ALL)

        response = auth_client.get('/employees/new/')
        assert response.status_code == 403

    # 管理者はGETでフォームを取得できることを確認
    def test_get_returns_form(self, admin_client):
        response = admin_client.get('/employees/new/')
        assert response.status_code == 200
        assert 'form' in response.context

    # 管理者が有効なデータでPOSTすると社員が作成され詳細ページにリダイレクトされることを確認
    def test_post_valid_data_creates_employee_and_redirects(self, admin_client):
        response = admin_client.post('/employees/new/', {
            'employee_number': 'E0099', 'last_name': '山田', 'first_name': '太郎', 'password': 'password123',
        })

        employee = Employee.objects.get(employee_number='E0099')
        assert response.status_code == 302
        assert response.url == f'/employees/{employee.id}/'

    # 社員の登録時にログイン用のUserも同時に作成されることを確認
    def test_post_valid_data_also_creates_user(self, admin_client):
        admin_client.post('/employees/new/', {
            'employee_number': 'E0099', 'last_name': '山田', 'first_name': '太郎', 'password': 'password123',
        })

        user = User.objects.get(username='E0099')
        assert user.last_name == '山田'
        assert user.first_name == '太郎'
        assert user.check_password('password123') is True

    # 社員番号が既に使われている場合、エラー付きでフォームが再表示されることを確認
    def test_post_duplicate_employee_number_redisplays_form_with_error(self, admin_client, sample_user):
        response = admin_client.post('/employees/new/', {
            'employee_number': 'E0001', 'last_name': '山田', 'first_name': '太郎', 'password': 'password123',
        })

        assert response.status_code == 200
        assert 'この社員番号は既に使用されています。' in response.context['form'].errors['employee_number']
        assert Employee.objects.filter(employee_number='E0001').count() == 1


@pytest.mark.django_db
class TestEmployeeEditView:

    # 編集権限が無いユーザーがアクセスすると403が返ることを確認
    def test_edit_by_user_without_permission_returns_403(self, sample_user, other_user, auth_client):
        _grant(sample_user, DEPARTMENT_VIEWER_ALL)

        response = auth_client.get(f'/employees/{other_user.employee.id}/edit/')
        assert response.status_code == 403

    # 存在しない社員の場合404が返ることを確認
    def test_edit_nonexistent_employee_returns_404(self, admin_client):
        response = admin_client.get('/employees/9999/edit/')
        assert response.status_code == 404


    # 管理者が有効なデータでPOSTすると氏名が更新され、パスワード未入力なら変更されないことを確認
    def test_post_valid_data_updates_name_without_changing_password(self, admin_client, sample_user):
        response = admin_client.post(f'/employees/{sample_user.employee.id}/edit/', {
            'employee_number': 'E0001', 'last_name': '鈴木', 'first_name': '花子', 'password': '',
        })

        sample_user.refresh_from_db()
        assert response.status_code == 302
        assert sample_user.last_name == '鈴木'
        assert sample_user.first_name == '花子'
        assert sample_user.check_password('testpass123') is True

    # パスワードを入力した場合はパスワードも更新されることを確認
    def test_post_with_password_updates_password(self, admin_client, sample_user):
        admin_client.post(f'/employees/{sample_user.employee.id}/edit/', {
            'employee_number': 'E0001', 'last_name': '鈴木', 'first_name': '花子', 'password': 'newpassword123',
        })

        sample_user.refresh_from_db()
        assert sample_user.check_password('newpassword123') is True

    # 他人の社員番号に変更しようとすると、エラー付きでフォームが再表示され更新されないことを確認
    def test_post_duplicate_employee_number_redisplays_form_with_error(self, admin_client, sample_user, other_user):
        employee = sample_user.employee

        response = admin_client.post(f'/employees/{employee.id}/edit/', {
            'employee_number': 'E0002', 'last_name': '鈴木', 'first_name': '花子', 'password': '',
        })

        employee.refresh_from_db()
        assert response.status_code == 200
        assert 'この社員番号は既に使用されています。' in response.context['form'].errors['employee_number']
        assert employee.employee_number == 'E0001'


@pytest.mark.django_db
class TestEmployeeDeleteView:

    # 削除権限が無いユーザーがアクセスすると403が返ることを確認
    def test_delete_by_user_without_permission_returns_403(self, sample_user, other_user, auth_client):
        _grant(sample_user, DEPARTMENT_VIEWER_ALL)

        response = auth_client.post(f'/employees/{other_user.employee.id}/delete/')
        assert response.status_code == 403

    # 管理者はPOSTで削除でき、一覧ページにリダイレクトされることを確認
    def test_post_deletes_employee_and_redirects_to_index(self, admin_client, other_user):
        response = admin_client.post(f'/employees/{other_user.employee.id}/delete/')

        assert response.status_code == 302
        assert response.url == '/employees/'


def _grant(user, permission_set_id):
    company = Company.objects.create(name=f'権限セット{permission_set_id}用の会社')
    department = Department.objects.create(company=company, name='権限セット用部門')
    EmployeeDepartment.objects.create(employee=user.employee, department=department, is_primary=True)
    group = ManagementGroup.objects.create(
        name=f'test-group-{permission_set_id}-{user.username}', department=department, permission_set_id=permission_set_id
    )
    group.members.add(user)
