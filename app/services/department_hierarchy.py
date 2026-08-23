from app import errors
from app.models import Department, DepartmentHierarchy


# 部門階層を作成する(親部門は同じ会社に属し、自分自身であってはならない)
def create(*, department: Department, parent_department: Department | None) -> DepartmentHierarchy:
    if parent_department is not None:
        _validate_parent_department(department=department, parent_department=parent_department)
    return DepartmentHierarchy.objects.create(department=department, parent_department=parent_department)


# 親部門を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_parent_department(*, department: Department, parent_department: Department) -> None:
    if parent_department.pk == department.pk:
        raise errors.department_hierarchy.SelfParentDepartmentError()
    if parent_department.company_id != department.company_id:
        raise errors.department_hierarchy.ParentDepartmentCompanyMismatchError()
