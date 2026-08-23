from app.errors.base import DomainError


# 同じ会社内に同名の部門が既に存在する
class DuplicateDepartmentNameError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_department_name', message='この会社には同じ名前の部門が既に存在します。')
