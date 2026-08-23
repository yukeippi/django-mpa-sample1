from app.errors.base import DomainError


# 管理グループ名が既に使用されている
class DuplicateManagementGroupNameError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_management_group_name', message='この管理グループ名は既に使用されています。')


# 全社管理者グループには部門を設定できない
class AdminGroupCannotHaveDepartmentError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code='admin_group_cannot_have_department', message='全社管理者グループには部門を設定できません。',
        )


# 全社管理者でない場合は部門の設定が必須
class NonAdminGroupRequiresDepartmentError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code='non_admin_group_requires_department', message='全社管理者でない場合は部門の設定が必須です。',
        )


# 全社管理者グループには権限セットを設定できない
class AdminGroupCannotHavePermissionSetError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code='admin_group_cannot_have_permission_set', message='全社管理者グループには権限セットを設定できません。',
        )


# 全社管理者でない場合は権限セットの設定が必須
class NonAdminGroupRequiresPermissionSetError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code='non_admin_group_requires_permission_set',
            message='全社管理者でない場合は権限セットの設定が必須です。',
        )


# 存在しない権限セット番号が指定された
class InvalidPermissionSetIdError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='invalid_permission_set_id', message='存在しない権限セット番号です。')
