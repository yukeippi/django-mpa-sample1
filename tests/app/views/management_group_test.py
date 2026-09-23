import pytest
from app.models import Company, Department, ManagementGroup


@pytest.mark.django_db
class TestManagementGroupIndexView:

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_index_requires_login(self, client):
        response = client.get('/management_groups/')
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # 管理者以外がアクセスすると403が返ること
    def test_index_by_non_admin_returns_403(self, auth_client):
        response = auth_client.get('/management_groups/')
        assert response.status_code == 403

    # 管理者は一覧を取得できること
    def test_index_by_admin_succeeds(self, admin_client):
        ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.get('/management_groups/')
        assert response.status_code == 200
        assert len(response.context['management_groups']) == 1


@pytest.mark.django_db
class TestManagementGroupShowView:

    # 管理者以外がアクセスすると403が返ること
    def test_show_by_non_admin_returns_403(self, auth_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = auth_client.get(f'/management_groups/{group.id}/')
        assert response.status_code == 403

    # 管理者は詳細を取得できること
    def test_show_by_admin_succeeds(self, admin_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.get(f'/management_groups/{group.id}/')
        assert response.status_code == 200
        assert response.context['management_group'] == group


@pytest.mark.django_db
class TestManagementGroupCreateView:

    # 管理者以外がアクセスすると403が返ること
    def test_new_by_non_admin_returns_403(self, auth_client):
        response = auth_client.get('/management_groups/new/')
        assert response.status_code == 403

    # 管理者はGETでフォームを取得できること
    def test_get_returns_form(self, admin_client):
        response = admin_client.get('/management_groups/new/')
        assert response.status_code == 200
        assert 'form' in response.context

    # 有効なデータでPOSTするとグループが作成され詳細ページにリダイレクトされること
    def test_post_valid_data_creates_group_and_redirects(self, admin_client, sample_user):
        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム',
            'members': [sample_user.id],
            'is_admin': True,
        })

        group = ManagementGroup.objects.get(name='開発チーム')
        assert response.status_code == 302
        assert response.url == f'/management_groups/{group.id}/'

    # 名前が重複する場合、エラー付きでフォームが再表示されること
    def test_post_duplicate_name_redisplays_form_with_error(self, admin_client):
        ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'is_admin': True,
        })

        assert response.status_code == 200
        assert 'この管理グループ名は既に使用されています。' in response.context['form'].errors['name']
        assert ManagementGroup.objects.filter(name='開発チーム').count() == 1

    # 全社管理者に部門を指定するとエラーになること
    def test_post_admin_group_with_department_redisplays_form_with_error(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'is_admin': True, 'department': department.id,
        })

        assert response.status_code == 200
        assert '全社管理者グループには部門を設定できません。' in response.context['form'].non_field_errors()

    # 全社管理者でないのに部門が未指定だとエラーになること
    def test_post_non_admin_group_without_department_redisplays_form_with_error(self, admin_client):
        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'permission_set_id': 1,
        })

        assert response.status_code == 200
        assert '全社管理者でない場合は部門の設定が必須です。' in response.context['form'].non_field_errors()

    # 全社管理者に権限セットを指定するとエラーになること
    def test_post_admin_group_with_permission_set_redisplays_form_with_error(self, admin_client):
        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'is_admin': True, 'permission_set_id': 1,
        })

        assert response.status_code == 200
        assert '全社管理者グループには権限セットを設定できません。' in response.context['form'].non_field_errors()

    # 全社管理者でないのに権限セットが未指定だとエラーになること
    def test_post_non_admin_group_without_permission_set_redisplays_form_with_error(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'department': department.id,
        })

        assert response.status_code == 200
        assert '全社管理者でない場合は権限セットの設定が必須です。' in response.context['form'].non_field_errors()

    # 存在しない権限セット番号を指定するとエラーになること
    def test_post_invalid_permission_set_id_redisplays_form_with_error(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='開発部')

        response = admin_client.post('/management_groups/new/', {
            'name': '開発チーム', 'members': [], 'department': department.id, 'permission_set_id': 999,
        })

        assert response.status_code == 200
        assert '存在しない権限セット番号です。' in response.context['form'].non_field_errors()


@pytest.mark.django_db
class TestManagementGroupEditView:

    # 管理者以外がアクセスすると403が返ること
    def test_edit_by_non_admin_returns_403(self, auth_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = auth_client.get(f'/management_groups/{group.id}/edit/')
        assert response.status_code == 403

    # 有効なデータでPOSTすると更新され詳細ページにリダイレクトされること
    def test_post_valid_data_updates_group_and_redirects(self, admin_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.post(f'/management_groups/{group.id}/edit/', {
            'name': '運用チーム',
            'members': [],
            'is_admin': True,
        })

        group.refresh_from_db()
        assert response.status_code == 302
        assert group.name == '運用チーム'

    # 他グループと名前が重複する場合、エラー付きでフォームが再表示され更新されないこと
    def test_post_duplicate_name_redisplays_form_with_error(self, admin_client):
        ManagementGroup.objects.create(name='運用チーム', is_admin=True)
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.post(f'/management_groups/{group.id}/edit/', {
            'name': '運用チーム', 'members': [], 'is_admin': True,
        })

        group.refresh_from_db()
        assert response.status_code == 200
        assert 'この管理グループ名は既に使用されています。' in response.context['form'].errors['name']
        assert group.name == '開発チーム'


@pytest.mark.django_db
class TestManagementGroupDeleteView:

    # 管理者以外がアクセスすると403が返ること
    def test_delete_by_non_admin_returns_403(self, auth_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = auth_client.post(f'/management_groups/{group.id}/delete/')
        assert response.status_code == 403
        assert ManagementGroup.objects.filter(id=group.id).count() == 1

    # 管理者はPOSTで削除でき、一覧ページにリダイレクトされること
    def test_post_deletes_group_and_redirects_to_index(self, admin_client):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        response = admin_client.post(f'/management_groups/{group.id}/delete/')

        assert response.status_code == 302
        assert response.url == '/management_groups/'
        assert ManagementGroup.objects.filter(id=group.id).count() == 0
