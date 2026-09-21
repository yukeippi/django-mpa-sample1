from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from app.lib.types import AuthenticatedHttpRequest
from app.forms import EmployeeForm
from app.models import Employee
from app.permissions.access import can_create, can_delete, can_display_create_form, can_edit, can_view

MODEL_NAME = 'Employee'


# 社員一覧
# 権限判定をPython側で行うため全件をメモリに展開してからフィルタする。件数が増えるとPaginatorの
# メリット(DBへのLIMIT/OFFSET)が失われるため、その場合はDB側で絞り込む方式への変更を検討する
@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    employees_qs = Employee.objects.with_user()
    employees = [employee for employee in employees_qs if can_view(request.user, MODEL_NAME, employee)]
    paginator = Paginator(employees, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/employee/index.html', {
        'employees': page_obj,
        'page_obj': page_obj,
    })


# 社員詳細
@login_required
def show(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if not can_view(request.user, MODEL_NAME, employee):
        raise PermissionDenied
    return render(request, 'app/employee/show.html', {'employee': employee})


# 社員新規作成
@login_required
def new(request: AuthenticatedHttpRequest) -> HttpResponse:
    if not can_display_create_form(request.user, MODEL_NAME):
        raise PermissionDenied
    if request.method == 'POST':
        return _create_employee(request)
    return _display_new_form(request)


# 社員編集
@login_required
def edit(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if not can_edit(request.user, MODEL_NAME, employee):
        raise PermissionDenied
    if request.method == 'POST':
        return _update_employee(request, employee)
    return _display_edit_form(request, employee)


# 社員削除
@login_required
def delete(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=pk)
    if not can_delete(request.user, MODEL_NAME, employee):
        raise PermissionDenied
    if request.method == 'POST':
        _delete_employee(employee=employee)
        messages.success(request, '社員情報を削除しました。')
        return redirect('app:employee_index')
    return render(request, 'app/employee/delete.html', {'employee': employee})


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 新規作成フォームを表示する
def _display_new_form(request):
    form = EmployeeForm(is_new=True)
    return _render_new_form(request, form)


# 社員の新規作成処理を行う(UserとEmployeeを同時作成)
def _create_employee(request):
    form = EmployeeForm(request.POST, is_new=True)
    if not form.is_valid():
        return _render_new_form(request, form)
    if not can_create(request.user, MODEL_NAME, form.instance):
        raise PermissionDenied
    employee = _save_new_employee(form=form)
    messages.success(request, '社員を登録しました。')
    return redirect('app:employee_show', pk=employee.pk)


# 社員新規作成フォームのレンダリング
def _render_new_form(request, form):
    return render(request, 'app/employee/new.html', {'form': form})


# 編集フォームを表示する
def _display_edit_form(request, employee):
    form = EmployeeForm(instance=employee)
    return _render_edit_form(request, employee, form)



# 社員の更新処理を行う
def _update_employee(request, employee):
    form = EmployeeForm(request.POST, instance=employee)
    if not form.is_valid():
        return _render_edit_form(request, employee, form)
    _save_employee_changes(form=form)
    messages.success(request, '社員情報を更新しました。')
    return redirect('app:employee_show', pk=employee.pk)


# 社員編集フォームのレンダリング
def _render_edit_form(request, employee, form):
    return render(request, 'app/employee/edit.html', {'form': form, 'employee': employee})


# UserとEmployeeを同時に作成する
@transaction.atomic
def _save_new_employee(*, form: EmployeeForm) -> Employee:
    user = User.objects.create_user(
        username=form.cleaned_data['employee_number'],
        first_name=form.cleaned_data['first_name'],
        last_name=form.cleaned_data['last_name'],
        password=form.cleaned_data['password'],
    )
    employee = form.save(commit=False)
    employee.user = user
    employee.save()
    return employee


# 社員情報を更新する(パスワードは入力があった場合のみ変更)
@transaction.atomic
def _save_employee_changes(*, form: EmployeeForm) -> Employee:
    employee = form.save()

    user = employee.user
    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    if form.cleaned_data['password']:
        user.set_password(form.cleaned_data['password'])
    user.save()
    return employee


# 社員を削除する(UserをCASCADEで削除すると、紐づくEmployeeも削除される)
@transaction.atomic
def _delete_employee(*, employee: Employee) -> None:
    employee.user.delete()

