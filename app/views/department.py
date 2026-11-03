from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from app.lib.types import AuthenticatedHttpRequest
from app.forms import DepartmentForm
from app.models import Department, DepartmentHierarchy
from app.permissions.access import can_create, can_delete, can_display_create_form, can_edit, can_view
from app.permissions.roles import is_company_admin

MODEL_NAME = 'Department'


# 部門一覧
# 権限判定をPython側で行うため全件をメモリに展開してからフィルタする。件数が増えるとPaginatorの
# メリット(DBへのLIMIT/OFFSET)が失われるため、その場合はDB側で絞り込む方式への変更を検討する
@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    departments_qs = Department.objects.with_company().order_by('company__name', 'name')
    departments = [department for department in departments_qs if can_view(request.user, MODEL_NAME, department)]
    paginator = Paginator(departments, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/department/index.html', {
        'departments': page_obj,
        'page_obj': page_obj,
    })


# 部門詳細
@login_required
def show(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    department = get_object_or_404(Department, pk=pk)
    if not can_view(request.user, MODEL_NAME, department):
        raise PermissionDenied
    hierarchy = DepartmentHierarchy.objects.select_related('parent_department__company').filter(
        department=department
    ).first()
    return render(request, 'app/department/show.html', {
        'department': department,
        'parent_department': hierarchy.parent_department if hierarchy else None,
        'child_departments': Department.objects.with_company().filter(
            hierarchy__parent_department=department
        ).order_by('name'),
        'can_manage_hierarchy': is_company_admin(request.user),
    })


# 部門新規作成
@login_required
def new(request: AuthenticatedHttpRequest) -> HttpResponse:
    if not can_display_create_form(request.user, MODEL_NAME):
        raise PermissionDenied
    if request.method == 'POST':
        return _create_department(request)
    return _display_new_form(request)


# 部門編集
@login_required
def edit(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    department = get_object_or_404(Department, pk=pk)
    if not can_edit(request.user, MODEL_NAME, department):
        raise PermissionDenied
    if request.method == 'POST':
        return _update_department(request, department)
    return _display_edit_form(request, department)


# 部門削除
@login_required
def delete(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    department = get_object_or_404(Department, pk=pk)
    if not can_delete(request.user, MODEL_NAME, department):
        raise PermissionDenied
    if request.method == 'POST':
        department.delete()
        messages.success(request, '部門を削除しました。')
        return redirect('app:department_index')
    return render(request, 'app/department/delete.html', {'department': department})


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 新規作成フォームを表示する
def _display_new_form(request):
    form = DepartmentForm()
    return _render_new_form(request, form)


# 部門の新規作成処理を行う
def _create_department(request):
    form = DepartmentForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    if not can_create(request.user, MODEL_NAME, form.instance):
        raise PermissionDenied
    department = form.save()
    messages.success(request, '部門を作成しました。')
    return redirect('app:department_show', pk=department.pk)


# 部門新規作成フォームのレンダリング
def _render_new_form(request, form):
    return render(request, 'app/department/new.html', {'form': form})


# 編集フォームを表示する
def _display_edit_form(request, department):
    form = DepartmentForm(instance=department)
    return _render_edit_form(request, department, form)



# 部門の更新処理を行う
def _update_department(request, department):
    form = DepartmentForm(request.POST, instance=department)
    if not form.is_valid():
        return _render_edit_form(request, department, form)
    form.save()
    messages.success(request, '部門情報を更新しました。')
    return redirect('app:department_show', pk=department.pk)


# 部門編集フォームのレンダリング
def _render_edit_form(request, department, form):
    return render(request, 'app/department/edit.html', {'form': form, 'department': department})

