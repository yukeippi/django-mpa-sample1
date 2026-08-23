from app.errors.base import DomainError


# 会社名が既に使用されている
class DuplicateCompanyNameError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_company_name')
