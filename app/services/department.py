from app import errors
from app.forms.department import DepartmentForm
from app.models import Department


# 部門を作成する
def create(*, form: DepartmentForm) -> Department:
    company = form.cleaned_data['company']
    name = form.cleaned_data['name']
    _validate_unique_name(company=company, name=name, exclude_pk=None)
    return Department.objects.create(company=company, name=name)


# 部門を更新する
def update(*, department: Department, form: DepartmentForm) -> Department:
    company = form.cleaned_data['company']
    name = form.cleaned_data['name']
    _validate_unique_name(company=company, name=name, exclude_pk=department.pk)
    department.company = company
    department.name = name
    department.save(update_fields=['company', 'name'])
    return department


# 部門を削除する
def delete(*, department: Department) -> None:
    department.delete()


# 部門名の重複を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_unique_name(*, company, name: str, exclude_pk: int | None) -> None:
    if Department.objects.duplicate_of(company=company, name=name, exclude_pk=exclude_pk).exists():
        raise errors.department.DuplicateDepartmentNameError()
