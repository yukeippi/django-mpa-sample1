from django.contrib.auth.models import User
from django.db import transaction
from app import errors
from app.forms.employee import EmployeeForm
from app.models import Employee


# 社員を新規登録する(UserとEmployeeを同時作成)
@transaction.atomic
def create(*, form: EmployeeForm) -> Employee:
    employee_number = form.cleaned_data['employee_number']
    _validate_unique_employee_number(employee_number=employee_number, exclude_pk=None)

    user = User.objects.create_user(
        username=employee_number,
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        password=form.cleaned_data['password'],
    )
    return Employee.objects.create(user=user, employee_number=employee_number)


# 社員情報を更新する(パスワードは入力があった場合のみ変更)
@transaction.atomic
def update(*, employee: Employee, form: EmployeeForm) -> Employee:
    employee_number = form.cleaned_data['employee_number']
    _validate_unique_employee_number(employee_number=employee_number, exclude_pk=employee.pk)

    employee.employee_number = employee_number
    employee.save(update_fields=['employee_number'])

    user = employee.user
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    if form.cleaned_data['password']:
        user.set_password(form.cleaned_data['password'])
    user.save()
    return employee


# 社員を削除する(UserをCASCADEで削除すると、紐づくEmployeeも削除される)
@transaction.atomic
def delete(*, employee: Employee) -> None:
    employee.user.delete()


# 社員番号の重複を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_unique_employee_number(*, employee_number: str, exclude_pk: int | None) -> None:
    duplicates = Employee.objects.filter(employee_number=employee_number)
    if exclude_pk is not None:
        duplicates = duplicates.exclude(pk=exclude_pk)
    if duplicates.exists():
        raise errors.employee.DuplicateEmployeeNumberError()
