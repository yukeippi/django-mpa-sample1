from app.errors.base import DomainError


# 同じ社員が同じ部門に既に所属している
class DuplicateEmployeeDepartmentError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_employee_department')
