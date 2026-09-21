from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from app.errors.base import DomainError
from app.errors.company import DuplicateCompanyNameError
from app.forms import CompanyForm
from app.models import Company
from app.permissions.access import can_create, can_delete, can_display_create_form, can_edit, can_view

MODEL_NAME = 'Company'


# 会社一覧
# 権限判定をPython側で行うため全件をメモリに展開してからフィルタする。件数が増えるとPaginatorの
# メリット(DBへのLIMIT/OFFSET)が失われるため、その場合はDB側で絞り込む方式への変更を検討する
@login_required
def index(request: HttpRequest) -> HttpResponse:
    companies_qs = Company.objects.all()
    companies = [company for company in companies_qs if can_view(request.user, MODEL_NAME, company)]
    paginator = Paginator(companies, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/company/index.html', {
        'companies': page_obj,
        'page_obj': page_obj,
    })


# 会社詳細
@login_required
def show(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    if not can_view(request.user, MODEL_NAME, company):
        raise PermissionDenied
    return render(request, 'app/company/show.html', {'company': company})


# 会社新規作成
@login_required
def new(request: HttpRequest) -> HttpResponse:
    if not can_display_create_form(request.user, MODEL_NAME):
        raise PermissionDenied
    if request.method == 'POST':
        return _create_company(request)
    return _display_new_form(request)


# 会社編集
@login_required
def edit(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    if not can_edit(request.user, MODEL_NAME, company):
        raise PermissionDenied
    if request.method == 'POST':
        return _update_company(request, company)
    return _display_edit_form(request, company)


# 会社削除
@login_required
def delete(request: HttpRequest, pk: int) -> HttpResponse:
    company = get_object_or_404(Company, pk=pk)
    if not can_delete(request.user, MODEL_NAME, company):
        raise PermissionDenied
    if request.method == 'POST':
        company.delete()
        messages.success(request, '会社を削除しました。')
        return redirect('app:company_index')
    return render(request, 'app/company/delete.html', {'company': company})


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 新規作成フォームを表示する
def _display_new_form(request):
    form = CompanyForm()
    return _render_new_form(request, form)


# 会社の新規作成処理を行う
def _create_company(request):
    form = CompanyForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    name = form.cleaned_data['name']
    if not can_create(request.user, MODEL_NAME, Company(name=name)):
        raise PermissionDenied
    try:
        _validate_unique_name(name=name, exclude_pk=None)
    except DomainError as error:
        form.add_error(None, error.message)
        return _render_new_form(request, form)
    company = Company.objects.create(name=name)
    messages.success(request, '会社を作成しました。')
    return redirect('app:company_show', pk=company.pk)


# 会社新規作成フォームのレンダリング
def _render_new_form(request, form):
    return render(request, 'app/company/new.html', {'form': form})


# 編集フォームを表示する
def _display_edit_form(request, company):
    form = CompanyForm(initial=_company_initial(company))
    return _render_edit_form(request, company, form)


# instanceの現在値からFormの初期値を組み立てる(ModelFormを使わないため明示的に行う)
def _company_initial(company):
    return {'name': company.name}


# 会社の更新処理を行う
def _update_company(request, company):
    form = CompanyForm(request.POST)
    if not form.is_valid():
        return _render_edit_form(request, company, form)
    name = form.cleaned_data['name']
    try:
        _validate_unique_name(name=name, exclude_pk=company.pk)
    except DomainError as error:
        form.add_error(None, error.message)
        return _render_edit_form(request, company, form)
    company.name = name
    company.save(update_fields=['name'])
    messages.success(request, '会社情報を更新しました。')
    return redirect('app:company_show', pk=company.pk)


# 会社編集フォームのレンダリング
def _render_edit_form(request, company, form):
    return render(request, 'app/company/edit.html', {'form': form, 'company': company})


# 会社名の重複を検証する(DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_unique_name(*, name: str, exclude_pk: int | None) -> None:
    duplicates = Company.objects.filter(name=name)
    if exclude_pk is not None:
        duplicates = duplicates.exclude(pk=exclude_pk)
    if duplicates.exists():
        raise DuplicateCompanyNameError()
