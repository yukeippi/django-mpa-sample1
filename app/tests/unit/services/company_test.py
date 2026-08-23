import pytest
from app.errors.company import DuplicateCompanyNameError
from app.forms.company import CompanyForm
from app.models import Company
from app.services import company as company_service


@pytest.mark.django_db
class TestCreate:

    # 有効なフォームから会社が作成されることを確認
    def test_creates_company(self):
        form = CompanyForm(data={'name': 'サンプル株式会社'})
        assert form.is_valid()

        company = company_service.create(form=form)

        assert company.id is not None
        assert company.name == 'サンプル株式会社'

    # 名前が重複する場合はDuplicateCompanyNameErrorが送出されることを確認
    def test_duplicate_name_raises_error(self):
        Company.objects.create(name='サンプル株式会社')
        form = CompanyForm(data={'name': 'サンプル株式会社'})
        assert form.is_valid()

        with pytest.raises(DuplicateCompanyNameError):
            company_service.create(form=form)


@pytest.mark.django_db
class TestUpdate:

    # 有効なフォームで会社が更新されることを確認
    def test_updates_company(self):
        company = Company.objects.create(name='元の会社')
        form = CompanyForm(data={'name': '更新後の会社'})
        assert form.is_valid()

        updated_company = company_service.update(company=company, form=form)

        assert updated_company.name == '更新後の会社'

    # 自分自身との重複はエラーにならないことを確認(名前を変更しない更新)
    def test_updating_with_same_name_does_not_raise_error(self):
        company = Company.objects.create(name='サンプル株式会社')
        form = CompanyForm(data={'name': 'サンプル株式会社'})
        assert form.is_valid()

        updated_company = company_service.update(company=company, form=form)

        assert updated_company.name == 'サンプル株式会社'

    # 他社と名前が重複する場合はDuplicateCompanyNameErrorが送出されることを確認
    def test_duplicate_name_raises_error(self):
        Company.objects.create(name='既存の会社')
        company = Company.objects.create(name='元の会社')
        form = CompanyForm(data={'name': '既存の会社'})
        assert form.is_valid()

        with pytest.raises(DuplicateCompanyNameError):
            company_service.update(company=company, form=form)


@pytest.mark.django_db
class TestDelete:

    # 会社が削除されることを確認
    def test_deletes_company(self):
        company = Company.objects.create(name='削除する会社')

        company_service.delete(company=company)

        assert Company.objects.filter(id=company.id).count() == 0
