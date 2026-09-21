from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from app.errors.base import DomainError
from app.errors.management_group import (
    AdminGroupCannotHaveDepartmentError,
    AdminGroupCannotHavePermissionSetError,
    DuplicateManagementGroupNameError,
    InvalidPermissionSetIdError,
    NonAdminGroupRequiresDepartmentError,
    NonAdminGroupRequiresPermissionSetError,
)
from app.forms import ManagementGroupForm
from app.models import ManagementGroup
from app.permissions import rule_sets
from app.permissions.roles import is_admin


# 管理グループ一覧
@login_required
def index(request: HttpRequest) -> HttpResponse:
    _require_admin(request)
    groups_qs = ManagementGroup.objects.all()
    paginator = Paginator(groups_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/management_group/index.html', {
        'management_groups': page_obj,
        'page_obj': page_obj,
    })


# 管理グループ詳細
@login_required
def show(request: HttpRequest, pk: int) -> HttpResponse:
    _require_admin(request)
    management_group = get_object_or_404(ManagementGroup, pk=pk)
    return render(request, 'app/management_group/show.html', {'management_group': management_group})


# 管理グループ新規作成
@login_required
def new(request: HttpRequest) -> HttpResponse:
    _require_admin(request)
    if request.method == 'POST':
        return _create_management_group(request)
    return _display_new_form(request)


# 管理グループ編集
@login_required
def edit(request: HttpRequest, pk: int) -> HttpResponse:
    _require_admin(request)
    management_group = get_object_or_404(ManagementGroup, pk=pk)
    if request.method == 'POST':
        return _update_management_group(request, management_group)
    return _display_edit_form(request, management_group)


# 管理グループ削除
@login_required
def delete(request: HttpRequest, pk: int) -> HttpResponse:
    _require_admin(request)
    management_group = get_object_or_404(ManagementGroup, pk=pk)
    if request.method == 'POST':
        management_group.delete()
        messages.success(request, '管理グループを削除しました。')
        return redirect('app:management_group_index')
    return render(request, 'app/management_group/delete.html', {'management_group': management_group})


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 管理グループの操作はis_staffのみ許可する
def _require_admin(request):
    if not is_admin(request.user):
        raise PermissionDenied


# 新規作成フォームを表示する
def _display_new_form(request):
    form = ManagementGroupForm()
    return _render_new_form(request, form)


# 管理グループの新規作成処理を行う
def _create_management_group(request):
    form = ManagementGroupForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    try:
        management_group = _save_new_management_group(form=form)
    except DomainError as error:
        form.add_error(None, error.message)
        return _render_new_form(request, form)
    messages.success(request, '管理グループを作成しました。')
    return redirect('app:management_group_show', pk=management_group.pk)


# 管理グループ新規作成フォームのレンダリング
def _render_new_form(request, form):
    return render(request, 'app/management_group/new.html', {'form': form})


# 編集フォームを表示する
def _display_edit_form(request, management_group):
    form = ManagementGroupForm(initial=_management_group_initial(management_group))
    return _render_edit_form(request, management_group, form)


# instanceの現在値からFormの初期値を組み立てる(ModelFormを使わないため明示的に行う)
def _management_group_initial(management_group):
    return {
        'name': management_group.name,
        'members': management_group.members.all(),
        'is_admin': management_group.is_admin,
        'department': management_group.department,
        'permission_set_id': management_group.permission_set_id,
    }


# 管理グループの更新処理を行う
def _update_management_group(request, management_group):
    form = ManagementGroupForm(request.POST)
    if not form.is_valid():
        return _render_edit_form(request, management_group, form)
    try:
        _save_management_group_changes(management_group=management_group, form=form)
    except DomainError as error:
        form.add_error(None, error.message)
        return _render_edit_form(request, management_group, form)
    messages.success(request, '管理グループを更新しました。')
    return redirect('app:management_group_show', pk=management_group.pk)


# 管理グループ編集フォームのレンダリング
def _render_edit_form(request, management_group, form):
    return render(request, 'app/management_group/edit.html', {
        'form': form, 'management_group': management_group,
    })


# 管理グループを作成する
@transaction.atomic
def _save_new_management_group(*, form: ManagementGroupForm) -> ManagementGroup:
    name = form.cleaned_data['name']
    group_is_admin = form.cleaned_data['is_admin']
    department = form.cleaned_data['department']
    permission_set_id = form.cleaned_data['permission_set_id']
    _validate(
        name=name, group_is_admin=group_is_admin, department=department,
        permission_set_id=permission_set_id, exclude_pk=None,
    )

    group = ManagementGroup.objects.create(
        name=name, is_admin=group_is_admin, department=department, permission_set_id=permission_set_id,
    )
    group.members.set(form.cleaned_data['members'])
    return group


# 管理グループを更新する
@transaction.atomic
def _save_management_group_changes(*, management_group: ManagementGroup, form: ManagementGroupForm) -> ManagementGroup:
    name = form.cleaned_data['name']
    group_is_admin = form.cleaned_data['is_admin']
    department = form.cleaned_data['department']
    permission_set_id = form.cleaned_data['permission_set_id']
    _validate(
        name=name, group_is_admin=group_is_admin, department=department,
        permission_set_id=permission_set_id, exclude_pk=management_group.pk,
    )

    management_group.name = name
    management_group.is_admin = group_is_admin
    management_group.department = department
    management_group.permission_set_id = permission_set_id
    management_group.save(update_fields=['name', 'is_admin', 'department', 'permission_set_id'])
    management_group.members.set(form.cleaned_data['members'])
    return management_group


# 管理グループの入力内容を検証する(DjangoのValidationErrorを介さずDomainErrorを直接送出する)
# 引数名をgroup_is_adminとしているのは、このモジュールがログインユーザー向けのis_admin()をimportしているため
def _validate(
    *, name: str, group_is_admin: bool, department, permission_set_id: int | None, exclude_pk: int | None
) -> None:
    _validate_unique_name(name=name, exclude_pk=exclude_pk)
    if group_is_admin and department is not None:
        raise AdminGroupCannotHaveDepartmentError()
    if not group_is_admin and department is None:
        raise NonAdminGroupRequiresDepartmentError()
    if group_is_admin and permission_set_id is not None:
        raise AdminGroupCannotHavePermissionSetError()
    if not group_is_admin and permission_set_id is None:
        raise NonAdminGroupRequiresPermissionSetError()
    if not group_is_admin and permission_set_id not in rule_sets.REGISTRY:
        raise InvalidPermissionSetIdError()


# 管理グループ名の重複を検証する
def _validate_unique_name(*, name: str, exclude_pk: int | None) -> None:
    duplicates = ManagementGroup.objects.filter(name=name)
    if exclude_pk is not None:
        duplicates = duplicates.exclude(pk=exclude_pk)
    if duplicates.exists():
        raise DuplicateManagementGroupNameError()
