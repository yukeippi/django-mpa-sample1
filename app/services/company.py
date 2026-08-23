from app import errors
from app.forms.company import CompanyForm
from app.models import Company


# 会社を作成する
def create(*, form: CompanyForm) -> Company:
    name = form.cleaned_data['name']
    _validate_unique_name(name=name, exclude_pk=None)
    return Company.objects.create(name=name)


# 会社を更新する
def update(*, company: Company, form: CompanyForm) -> Company:
    name = form.cleaned_data['name']
    _validate_unique_name(name=name, exclude_pk=company.pk)
    company.name = name
    company.save(update_fields=['name'])
    return company


# 会社を削除する
def delete(*, company: Company) -> None:
    company.delete()


# 会社名の重複を検証する(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
def _validate_unique_name(*, name: str, exclude_pk: int | None) -> None:
    duplicates = Company.objects.filter(name=name)
    if exclude_pk is not None:
        duplicates = duplicates.exclude(pk=exclude_pk)
    if duplicates.exists():
        raise errors.company.DuplicateCompanyNameError()
