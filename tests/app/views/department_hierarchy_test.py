import pytest
from app.models import Company, Department, DepartmentHierarchy, ManagementGroup


# admin_client(pytest-djangoのis_staffユーザー)を、全社管理者グループ(ManagementGroup.is_admin)にも所属させる
@pytest.fixture(autouse=True)
def _grant_group_admin(admin_user):
    group = ManagementGroup.objects.create(name='test-admin-group', is_admin=True)
    group.members.add(admin_user)


@pytest.mark.django_db
class TestDepartmentHierarchyEditView:

    # 全社管理者は変更フォームを表示できること
    def test_get_by_admin_displays_form(self, admin_client):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')

        response = admin_client.get(f'/departments/{department.pk}/hierarchy/edit/')

        assert response.status_code == 200

    # 変更フォームを開くと、今の親部門が選ばれた状態になっていること
    def test_get_selects_current_parent(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        parent = Department.objects.create(company=company, name='本社')
        DepartmentHierarchy.objects.create(department=department, parent_department=parent)

        response = admin_client.get(f'/departments/{department.pk}/hierarchy/edit/')

        assert response.context['form']['parent_department'].value() == parent.pk

    # 親部門が無い部門の変更フォームを開くと、「なし」が選ばれた状態になっていること
    def test_get_without_parent_selects_none(self, admin_client):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')

        response = admin_client.get(f'/departments/{department.pk}/hierarchy/edit/')

        assert response.context['form']['parent_department'].value() is None

    # 親部門を選んで保存すると親部門が設定され、部門詳細画面にリダイレクトされること
    def test_post_sets_parent_and_redirects_to_department(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        parent = Department.objects.create(company=company, name='本社')

        response = admin_client.post(f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': parent.pk})

        assert response.status_code == 302
        assert response.url == f'/departments/{department.pk}/'
        assert DepartmentHierarchy.objects.get(department=department).parent_department == parent

    # 既に親部門がある部門でも、別の親部門に変更できること
    def test_post_changes_existing_parent(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(
            department=department, parent_department=Department.objects.create(company=company, name='本社')
        )
        new_parent = Department.objects.create(company=company, name='営業本部')

        admin_client.post(f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': new_parent.pk})

        assert DepartmentHierarchy.objects.get(department=department).parent_department == new_parent

    # 保存すると「親部門を変更しました。」が表示されること
    def test_post_shows_success_message(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        parent = Department.objects.create(company=company, name='本社')

        response = admin_client.post(
            f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': parent.pk}, follow=True
        )

        assert '親部門を変更しました。' in [str(message) for message in response.context['messages']]

    # 「なし」を選んで保存すると、親部門が無い状態になること
    def test_post_none_clears_parent(self, admin_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        DepartmentHierarchy.objects.create(
            department=department, parent_department=Department.objects.create(company=company, name='本社')
        )

        admin_client.post(f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': ''})

        assert DepartmentHierarchy.objects.get(department=department).parent_department is None

    # 別の会社の部門を送信するとフォームが再表示され、親部門は変わらないこと
    def test_post_parent_in_other_company_is_rejected(self, admin_client):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')
        other_company_department = Department.objects.create(
            company=Company.objects.create(name='テスト工業株式会社'), name='総務部'
        )

        response = admin_client.post(
            f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': other_company_department.pk}
        )

        assert response.status_code == 200
        assert 'parent_department' in response.context['form'].errors
        assert not DepartmentHierarchy.objects.filter(department=department).exists()

    # 全社管理者でないユーザーは変更フォームを表示できないこと(403)
    def test_get_by_non_admin_returns_403(self, auth_client):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')

        response = auth_client.get(f'/departments/{department.pk}/hierarchy/edit/')

        assert response.status_code == 403

    # 全社管理者でないユーザーは保存できず(403)、親部門は変わらないこと
    def test_post_by_non_admin_returns_403_and_does_not_change(self, auth_client):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        parent = Department.objects.create(company=company, name='本社')

        response = auth_client.post(f'/departments/{department.pk}/hierarchy/edit/', {'parent_department': parent.pk})

        assert response.status_code == 403
        assert not DepartmentHierarchy.objects.filter(department=department).exists()

    # 存在しない部門は404になること
    def test_nonexistent_department_returns_404(self, admin_client):
        response = admin_client.get('/departments/99999/hierarchy/edit/')

        assert response.status_code == 404

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_requires_login(self, client):
        department = Department.objects.create(company=Company.objects.create(name='サンプル株式会社'), name='営業部')

        response = client.get(f'/departments/{department.pk}/hierarchy/edit/')

        assert response.status_code == 302
        assert response.url.startswith('/login/')
