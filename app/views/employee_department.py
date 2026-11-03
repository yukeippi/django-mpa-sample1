from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from app.forms import EmployeeDepartmentForm
from app.lib.types import AuthenticatedHttpRequest
from app.models import Employee, EmployeeDepartment
from app.permissions.roles import is_company_admin


# 所属部門の追加
@login_required
def new(request: AuthenticatedHttpRequest, employee_pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=employee_pk)
    if not is_company_admin(request.user):
        raise PermissionDenied
    if request.method == 'POST':
        return _add_employee_department(request, employee)
    return _display_new_form(request, employee)


# 所属部門を外す(社員詳細画面のボタンから送信する。画面を持たないためPOSTのみ)
@login_required
@require_POST
def delete(request: AuthenticatedHttpRequest, employee_pk: int, pk: int) -> HttpResponse:
    employee = get_object_or_404(Employee, pk=employee_pk)
    relation = get_object_or_404(EmployeeDepartment, pk=pk, employee=employee)
    if not is_company_admin(request.user):
        raise PermissionDenied
    relation.delete()
    messages.success(request, '所属部門を外しました。')
    return redirect('app:employee_show', pk=employee.pk)


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 追加フォームを表示する
def _display_new_form(request, employee):
    form = EmployeeDepartmentForm(instance=EmployeeDepartment(employee=employee))
    return _render_new_form(request, employee, form)


# 所属部門の追加処理を行う
def _add_employee_department(request, employee):
    form = EmployeeDepartmentForm(request.POST, instance=EmployeeDepartment(employee=employee))
    if not form.is_valid():
        return _render_new_form(request, employee, form)
    form.save()
    messages.success(request, '所属部門を追加しました。')
    return redirect('app:employee_show', pk=employee.pk)


# 追加フォームのレンダリング
def _render_new_form(request, employee, form):
    return render(request, 'app/employee_department/new.html', {'form': form, 'employee': employee})
