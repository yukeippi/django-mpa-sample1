from django.db import transaction
from app import errors
from app.forms.management_group import ManagementGroupForm
from app.models import ManagementGroup
from app.permissions import rule_sets


# 管理グループを作成する
@transaction.atomic
def create(*, form: ManagementGroupForm) -> ManagementGroup:
    name = form.cleaned_data['name']
    is_admin = form.cleaned_data['is_admin']
    department = form.cleaned_data['department']
    permission_set_id = form.cleaned_data['permission_set_id']
    _validate(name=name, is_admin=is_admin, department=department, permission_set_id=permission_set_id, exclude_pk=None)

    group = ManagementGroup.objects.create(
        name=name, is_admin=is_admin, department=department, permission_set_id=permission_set_id,
    )
    group.members.set(form.cleaned_data['members'])
    return group


# 管理グループを更新する
@transaction.atomic
def update(*, management_group: ManagementGroup, form: ManagementGroupForm) -> ManagementGroup:
    name = form.cleaned_data['name']
    is_admin = form.cleaned_data['is_admin']
    department = form.cleaned_data['department']
    permission_set_id = form.cleaned_data['permission_set_id']
    _validate(
        name=name, is_admin=is_admin, department=department, permission_set_id=permission_set_id,
        exclude_pk=management_group.pk,
    )

    management_group.name = name
    management_group.is_admin = is_admin
    management_group.department = department
    management_group.permission_set_id = permission_set_id
    management_group.save(update_fields=['name', 'is_admin', 'department', 'permission_set_id'])
    management_group.members.set(form.cleaned_data['members'])
    return management_group


# 管理グループを削除する
def delete(*, management_group: ManagementGroup) -> None:
    management_group.delete()


# 管理グループの入力内容を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate(*, name: str, is_admin: bool, department, permission_set_id: int | None, exclude_pk: int | None) -> None:
    _validate_unique_name(name=name, exclude_pk=exclude_pk)
    if is_admin and department is not None:
        raise errors.management_group.AdminGroupCannotHaveDepartmentError()
    if not is_admin and department is None:
        raise errors.management_group.NonAdminGroupRequiresDepartmentError()
    if is_admin and permission_set_id is not None:
        raise errors.management_group.AdminGroupCannotHavePermissionSetError()
    if not is_admin and permission_set_id is None:
        raise errors.management_group.NonAdminGroupRequiresPermissionSetError()
    if not is_admin and permission_set_id not in rule_sets.REGISTRY:
        raise errors.management_group.InvalidPermissionSetIdError()


# 管理グループ名の重複を検証する
def _validate_unique_name(*, name: str, exclude_pk: int | None) -> None:
    duplicates = ManagementGroup.objects.filter(name=name)
    if exclude_pk is not None:
        duplicates = duplicates.exclude(pk=exclude_pk)
    if duplicates.exists():
        raise errors.management_group.DuplicateManagementGroupNameError()
