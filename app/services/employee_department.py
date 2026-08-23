from django.db import transaction
from app import errors
from app.models import Department, Employee, EmployeeDepartment


# 社員の所属部門を追加する(主務の場合、既存の主務は兼務に切り替える)
@transaction.atomic
def create(*, employee: Employee, department: Department, is_primary: bool = False) -> EmployeeDepartment:
    _validate_unique_employee_department(employee=employee, department=department)
    if is_primary:
        _demote_existing_primary(employee=employee)
    return EmployeeDepartment.objects.create(employee=employee, department=department, is_primary=is_primary)


# 社員・部門の組み合わせの重複を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_unique_employee_department(*, employee: Employee, department: Department) -> None:
    if EmployeeDepartment.objects.duplicate_of(employee=employee, department=department).exists():
        raise errors.employee_department.DuplicateEmployeeDepartmentError()


# 既存の主務を兼務に切り替える
def _demote_existing_primary(*, employee: Employee) -> None:
    EmployeeDepartment.objects.filter(employee=employee, is_primary=True).update(is_primary=False)
