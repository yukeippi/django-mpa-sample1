import pytest
from playwright.sync_api import Page, expect
from app.models import Company, Department


# 部門詳細画面から親部門を設定し、外すまでの一連のE2Eテスト
@pytest.mark.django_db
class TestDepartmentHierarchyFlow:

    # 詳細画面から親部門を設定すると詳細に表示され、「なし」にすると「親部門はありません」に戻ること
    def test_set_and_clear_parent_department(self, logged_in_page: Page, live_server_url):
        company = Company.objects.create(name='サンプル株式会社')
        department = Department.objects.create(company=company, name='営業部')
        Department.objects.create(company=company, name='本社')
        logged_in_page.goto(f'{live_server_url}/departments/{department.pk}/')

        logged_in_page.click('#edit-department-hierarchy-link')
        logged_in_page.select_option('#id_parent_department', label='サンプル株式会社 / 本社')
        logged_in_page.click('#department-hierarchy-form-submit')

        expect(logged_in_page.locator('#department-parent')).to_have_text('サンプル株式会社 / 本社')

        logged_in_page.click('#edit-department-hierarchy-link')
        logged_in_page.select_option('#id_parent_department', label='なし')
        logged_in_page.click('#department-hierarchy-form-submit')

        expect(logged_in_page.locator('#department-parent')).to_have_text('親部門はありません')
