from app.errors.base import DomainError


# 社員番号が既に使用されている
class DuplicateEmployeeNumberError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_employee_number')
