import pytest
from app.forms.company import CompanyForm


# CompanyFormのテストクラス
@pytest.mark.django_db
class TestCompanyForm:

    # 有効なデータでフォームが妥当と判定されること
    def test_valid_data_is_valid(self):
        form = CompanyForm(data={'name': 'サンプル株式会社'})
        assert form.is_valid()

    # 名前が空の場合、フォームが無効と判定されること
    def test_blank_name_is_invalid(self):
        form = CompanyForm(data={'name': ''})
        assert not form.is_valid()
        assert 'name' in form.errors
