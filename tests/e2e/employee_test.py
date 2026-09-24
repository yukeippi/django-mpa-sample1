import pytest
from playwright.sync_api import Page, expect
from app.models import Company, Department


# 社員の新規作成〜詳細確認〜編集〜削除までの一連のE2Eテスト
@pytest.mark.django_db
class TestEmployeeCrudFlow:

    # 新規作成フォームから社員を登録すると詳細ページに遷移すること
    def test_create_employee_and_view_detail(self, logged_in_page: Page, live_server_url):
        logged_in_page.goto(f'{live_server_url}/employees/new/')

        logged_in_page.fill('#id_employee_number', 'E9100')
        logged_in_page.fill('#id_last_name', '山田')
        logged_in_page.fill('#id_first_name', '太郎')
        logged_in_page.fill('#id_password', 'pass12345')
        logged_in_page.click('#employee-form-submit')

        expect(logged_in_page.locator('#employee-number')).to_have_text('E9100')
        expect(logged_in_page.locator('#employee-full-name')).to_contain_text('太郎')

    # 詳細ページから編集し、氏名が更新されること
    def test_edit_employee_updates_name(self, logged_in_page: Page, live_server_url):
        logged_in_page.goto(f'{live_server_url}/employees/new/')
        logged_in_page.fill('#id_employee_number', 'E9200')
        logged_in_page.fill('#id_last_name', '鈴木')
        logged_in_page.fill('#id_first_name', '花子')
        logged_in_page.fill('#id_password', 'pass12345')
        logged_in_page.click('#employee-form-submit')

        logged_in_page.click('#edit-employee-link')
        logged_in_page.fill('#id_last_name', '佐藤')
        logged_in_page.click('#employee-form-submit')

        expect(logged_in_page.locator('#employee-full-name')).to_contain_text('佐藤')

    # 削除確認ページから削除すると一覧ページに戻り、対象が表示されなくなること
    def test_delete_employee_removes_from_list(self, logged_in_page: Page, live_server_url):
        logged_in_page.goto(f'{live_server_url}/employees/new/')
        logged_in_page.fill('#id_employee_number', 'E9300')
        logged_in_page.fill('#id_last_name', '田中')
        logged_in_page.fill('#id_first_name', '一郎')
        logged_in_page.fill('#id_password', 'pass12345')
        logged_in_page.click('#employee-form-submit')

        logged_in_page.click('#delete-employee-link')
        logged_in_page.click('#employee-delete-confirm')

        expect(logged_in_page).to_have_url(f'{live_server_url}/employees/')
        expect(logged_in_page.locator('#employee-table')).not_to_contain_text('E9300')


# 社員詳細画面から所属部門を追加し、外すまでの一連のE2Eテスト
@pytest.mark.django_db
class TestEmployeeDepartmentFlow:

    # 詳細画面から部門を主務として追加すると一覧に表示され、外すと一覧から消えること
    def test_add_and_remove_department(self, logged_in_page: Page, live_server_url, e2e_user):
        company = Company.objects.create(name='サンプル株式会社')
        Department.objects.create(company=company, name='開発部')
        logged_in_page.goto(f'{live_server_url}/employees/{e2e_user.employee.pk}/')

        logged_in_page.click('#add-employee-department-link')
        logged_in_page.select_option('#id_department', label='サンプル株式会社 / 開発部')
        logged_in_page.check('#id_is_primary')
        logged_in_page.click('#employee-department-form-submit')

        expect(logged_in_page.locator('#employee-departments')).to_contain_text('サンプル株式会社 / 開発部')
        expect(logged_in_page.locator('#employee-departments')).to_contain_text('主務')

        logged_in_page.click('.remove-employee-department')

        expect(logged_in_page.locator('#employee-no-departments')).to_have_text('所属部門はありません')


# 未ログイン時のアクセス制御に関するE2Eテスト
@pytest.mark.django_db
class TestEmployeeAccessControl:

    # 未ログインで社員一覧にアクセスするとログインページにリダイレクトされること
    def test_employee_index_redirects_anonymous_user_to_login(self, page: Page, live_server_url):
        page.goto(f'{live_server_url}/employees/')
        expect(page).to_have_url(f'{live_server_url}/login/?next=/employees/')
