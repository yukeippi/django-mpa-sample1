from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from app.forms import DepartmentHierarchyForm
from app.lib.types import AuthenticatedHttpRequest
from app.models import Department, DepartmentHierarchy
from app.permissions.roles import is_company_admin


# 親部門の変更(親子関係は管理グループが効く範囲を左右するため、全社管理者だけに許可する)
@login_required
def edit(request: AuthenticatedHttpRequest, department_pk: int) -> HttpResponse:
    department = get_object_or_404(Department, pk=department_pk)
    if not is_company_admin(request.user):
        raise PermissionDenied
    # 階層レコードを持たない部門もあるため、無ければ未保存のレコードを作って保存時に新規作成する
    hierarchy = DepartmentHierarchy.objects.filter(department=department).first() or DepartmentHierarchy(
        department=department
    )
    if request.method == 'POST':
        return _update_hierarchy(request, department, hierarchy)
    return _display_edit_form(request, department, hierarchy)


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 変更フォームを表示する
def _display_edit_form(request, department, hierarchy):
    form = DepartmentHierarchyForm(instance=hierarchy)
    return _render_edit_form(request, department, form)


# 親部門の変更処理を行う
def _update_hierarchy(request, department, hierarchy):
    form = DepartmentHierarchyForm(request.POST, instance=hierarchy)
    if not form.is_valid():
        return _render_edit_form(request, department, form)
    form.save()
    messages.success(request, '親部門を変更しました。')
    return redirect('app:department_show', pk=department.pk)


# 変更フォームのレンダリング
def _render_edit_form(request, department, form):
    return render(request, 'app/department_hierarchy/edit.html', {'form': form, 'department': department})
