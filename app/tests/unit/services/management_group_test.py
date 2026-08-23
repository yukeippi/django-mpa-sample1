import pytest
from app.errors.management_group import (
    AdminGroupCannotHaveDepartmentError,
    AdminGroupCannotHavePermissionSetError,
    DuplicateManagementGroupNameError,
    InvalidPermissionSetIdError,
    NonAdminGroupRequiresDepartmentError,
    NonAdminGroupRequiresPermissionSetError,
)
from app.forms.management_group import ManagementGroupForm
from app.models import Company, Department, ManagementGroup
from app.services import management_group as management_group_service


@pytest.mark.django_db
class TestCreate:

    # 有効なフォームから管理グループが作成されることを確認
    def test_creates_management_group(self, sample_user):
        form = ManagementGroupForm(data={'name': '開発チーム', 'members': [sample_user.id], 'is_admin': True})
        assert form.is_valid()

        management_group = management_group_service.create(form=form)

        assert management_group.id is not None
        assert management_group.name == '開発チーム'
        assert list(management_group.members.all()) == [sample_user]

    # 名前が重複する場合はDuplicateManagementGroupNameErrorが送出されることを確認
    def test_duplicate_name_raises_error(self):
        ManagementGroup.objects.create(name='開発チーム', is_admin=True)
        form = ManagementGroupForm(data={'name': '開発チーム', 'members': [], 'is_admin': True})
        assert form.is_valid()

        with pytest.raises(DuplicateManagementGroupNameError):
            management_group_service.create(form=form)

    # 全社管理者に部門を設定するとAdminGroupCannotHaveDepartmentErrorが送出されることを確認
    def test_admin_with_department_raises_error(self, sample_department):
        form = ManagementGroupForm(
            data={'name': '開発チーム', 'members': [], 'is_admin': True, 'department': sample_department.id}
        )
        assert form.is_valid()

        with pytest.raises(AdminGroupCannotHaveDepartmentError):
            management_group_service.create(form=form)

    # 全社管理者でないのに部門が未指定だとNonAdminGroupRequiresDepartmentErrorが送出されることを確認
    def test_non_admin_without_department_raises_error(self):
        form = ManagementGroupForm(
            data={'name': '開発チーム', 'members': [], 'is_admin': False, 'permission_set_id': 1}
        )
        assert form.is_valid()

        with pytest.raises(NonAdminGroupRequiresDepartmentError):
            management_group_service.create(form=form)

    # 全社管理者に権限セットを設定するとAdminGroupCannotHavePermissionSetErrorが送出されることを確認
    def test_admin_with_permission_set_raises_error(self):
        form = ManagementGroupForm(
            data={'name': '開発チーム', 'members': [], 'is_admin': True, 'permission_set_id': 1}
        )
        assert form.is_valid()

        with pytest.raises(AdminGroupCannotHavePermissionSetError):
            management_group_service.create(form=form)

    # 全社管理者でないのに権限セットが未指定だとNonAdminGroupRequiresPermissionSetErrorが送出されることを確認
    def test_non_admin_without_permission_set_raises_error(self, sample_department):
        form = ManagementGroupForm(
            data={'name': '開発チーム', 'members': [], 'is_admin': False, 'department': sample_department.id}
        )
        assert form.is_valid()

        with pytest.raises(NonAdminGroupRequiresPermissionSetError):
            management_group_service.create(form=form)

    # REGISTRYに存在しない権限セット番号を指定するとInvalidPermissionSetIdErrorが送出されることを確認
    def test_unknown_permission_set_id_raises_error(self, sample_department):
        form = ManagementGroupForm(data={
            'name': '開発チーム', 'members': [], 'is_admin': False,
            'department': sample_department.id, 'permission_set_id': 999,
        })
        assert form.is_valid()

        with pytest.raises(InvalidPermissionSetIdError):
            management_group_service.create(form=form)


@pytest.mark.django_db
class TestUpdate:

    # 有効なフォームで管理グループが更新されることを確認
    def test_updates_management_group(self):
        management_group = ManagementGroup.objects.create(name='元のチーム', is_admin=True)
        form = ManagementGroupForm(data={'name': '更新後のチーム', 'members': [], 'is_admin': True})
        assert form.is_valid()

        updated_group = management_group_service.update(management_group=management_group, form=form)

        assert updated_group.name == '更新後のチーム'

    # 他グループと名前が重複する場合はDuplicateManagementGroupNameErrorが送出されることを確認
    def test_duplicate_name_raises_error(self):
        ManagementGroup.objects.create(name='既存のチーム', is_admin=True)
        management_group = ManagementGroup.objects.create(name='元のチーム', is_admin=True)
        form = ManagementGroupForm(data={'name': '既存のチーム', 'members': [], 'is_admin': True})
        assert form.is_valid()

        with pytest.raises(DuplicateManagementGroupNameError):
            management_group_service.update(management_group=management_group, form=form)


@pytest.mark.django_db
class TestDelete:

    # 管理グループが削除されることを確認
    def test_deletes_management_group(self):
        management_group = ManagementGroup.objects.create(name='削除するチーム', is_admin=True)

        management_group_service.delete(management_group=management_group)

        assert ManagementGroup.objects.filter(id=management_group.id).count() == 0


@pytest.fixture
def sample_department():
    company = Company.objects.create(name='サンプル株式会社')
    return Department.objects.create(company=company, name='開発部')
