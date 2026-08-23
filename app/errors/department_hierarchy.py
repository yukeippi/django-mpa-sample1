from app.errors.base import DomainError


# 親部門が同じ会社に属していない
class ParentDepartmentCompanyMismatchError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='parent_department_company_mismatch')


# 親部門に自分自身を指定しようとした
class SelfParentDepartmentError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='self_parent_department')
