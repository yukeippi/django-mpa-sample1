import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from app.models import Company, Department, ManagementGroup


# ManagementGroupモデルのテストクラス
@pytest.mark.django_db
class TestManagementGroupModel:

    # is_admin=Trueなら部門なしでグループを作成できること
    def test_create_admin_group_without_department(self):
        group = ManagementGroup.objects.create(name='全社管理者グループ', is_admin=True)

        assert group.id is not None
        assert group.name == '全社管理者グループ'
        assert group.department is None

    # is_admin=Falseの場合は部門・権限セット番号を指定してグループを作成できること
    def test_create_non_admin_group_with_department(self):
        department = _create_department('開発部')

        group = ManagementGroup.objects.create(name='開発部管理グループ', department=department, permission_set_id=1)

        assert group.id is not None
        assert group.is_admin is False
        assert group.department == department

    # is_admin=Falseなのに部門が未設定の場合はエラーになること(DB制約)
    def test_department_required_when_not_admin(self):
        with pytest.raises(IntegrityError):
            ManagementGroup.objects.create(name='不正なグループ', permission_set_id=1)

    # is_admin=Trueなのに部門が設定されている場合はエラーになること(DB制約)
    def test_department_forbidden_when_admin(self):
        department = _create_department('開発部')

        with pytest.raises(IntegrityError):
            ManagementGroup.objects.create(name='不正なグループ', is_admin=True, department=department)

    # is_admin=Falseなのに権限セット番号が未設定の場合はエラーになること(DB制約)
    def test_permission_set_id_required_when_not_admin(self):
        department = _create_department('開発部')

        with pytest.raises(IntegrityError):
            ManagementGroup.objects.create(name='不正なグループ', department=department)

    # is_admin=Trueなのに権限セット番号が設定されている場合はエラーになること(DB制約)
    def test_permission_set_id_forbidden_when_admin(self):
        with pytest.raises(IntegrityError):
            ManagementGroup.objects.create(name='不正なグループ', is_admin=True, permission_set_id=1)

    # REGISTRYに存在する権限セット番号を指定した場合は作成できること
    def test_valid_permission_set_id_is_accepted(self):
        department = _create_department('開発部')

        group = ManagementGroup.objects.create(name='開発部管理グループ2', department=department, permission_set_id=1)

        assert group.permission_set_id == 1

    # 名前が重複する場合はエラーになること(DB制約)
    def test_name_must_be_unique(self):
        ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        with pytest.raises(IntegrityError):
            ManagementGroup.objects.create(name='開発チーム', is_admin=True)

    # 全社管理者に部門を設定すると、full_clean()で対応する文言のエラーになること
    def test_full_clean_rejects_admin_with_department(self):
        group = ManagementGroup(name='不正なグループ', is_admin=True, department=_create_department('開発部'))

        assert '全社管理者グループには部門を設定できません。' in _full_clean_messages(group)

    # 全社管理者でないのに部門が未設定だと、full_clean()で対応する文言のエラーになること
    def test_full_clean_rejects_non_admin_without_department(self):
        group = ManagementGroup(name='不正なグループ', permission_set_id=1)

        assert '全社管理者でない場合は部門の設定が必須です。' in _full_clean_messages(group)

    # 全社管理者に権限セット番号を設定すると、full_clean()で対応する文言のエラーになること
    def test_full_clean_rejects_admin_with_permission_set(self):
        group = ManagementGroup(name='不正なグループ', is_admin=True, permission_set_id=1)

        assert '全社管理者グループには権限セットを設定できません。' in _full_clean_messages(group)

    # 全社管理者でないのに権限セット番号が未設定だと、full_clean()で対応する文言のエラーになること
    def test_full_clean_rejects_non_admin_without_permission_set(self):
        group = ManagementGroup(name='不正なグループ', department=_create_department('開発部'))

        assert '全社管理者でない場合は権限セットの設定が必須です。' in _full_clean_messages(group)

    # REGISTRYに存在しない権限セット番号は、full_clean()でエラーになりcodeで識別できること
    def test_full_clean_rejects_unknown_permission_set_id(self):
        group = ManagementGroup(name='不正なグループ', department=_create_department('開発部'), permission_set_id=999)

        with pytest.raises(ValidationError) as error:
            group.full_clean()
        codes = [e.code for e in error.value.error_dict['__all__']]
        assert 'management_group_unknown_permission_set' in codes

    # 整合性を満たす全社管理者でないグループは、full_clean()を通ること
    def test_full_clean_accepts_valid_non_admin_group(self):
        group = ManagementGroup(name='開発部管理グループ', department=_create_department('開発部'), permission_set_id=1)

        group.full_clean()

    # メンバーを複数のユーザーで構成できること
    def test_members_can_have_multiple_users(self, sample_user, other_user):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)
        group.members.add(sample_user, other_user)

        assert group.members.count() == 2

    # __str__が名前を返すこと
    def test_str_returns_name(self):
        group = ManagementGroup.objects.create(name='開発チーム', is_admin=True)

        assert str(group) == '開発チーム'


def _full_clean_messages(group):
    with pytest.raises(ValidationError) as error:
        group.full_clean()
    return error.value.messages


def _create_department(name):
    company = Company.objects.create(name=f'{name}の会社')
    return Department.objects.create(company=company, name=name)
