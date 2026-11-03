import pytest
from app.forms.management_group import ManagementGroupForm
from app.models import Company, Department


# ManagementGroupFormのテストクラス
@pytest.mark.django_db
class TestManagementGroupForm:

    # 全社管理者として有効なデータでフォームが妥当と判定されること
    def test_valid_data_is_valid(self, sample_user):
        form = ManagementGroupForm(data={
            'name': '開発チーム',
            'members': [sample_user.id],
            'is_admin': True,
        })
        assert form.is_valid()

    # 名前が空の場合、フォームが無効と判定されること
    def test_blank_name_is_invalid(self):
        form = ManagementGroupForm(data={
            'name': '',
            'members': [],
            'is_admin': True,
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    # メンバー未選択でも妥当と判定されること(members=blank許可)
    def test_no_members_is_valid(self):
        form = ManagementGroupForm(data={
            'name': '開発チーム',
            'members': [],
            'is_admin': True,
        })
        assert form.is_valid()

    # 全社管理者でなく、部門・権限セット番号を指定していれば妥当と判定されること
    # (is_adminと部門・権限セットの整合性そのものはモデル側の担当のため、tests/app/models/で網羅する)
    def test_valid_non_admin_data_is_valid(self, sample_department):
        form = ManagementGroupForm(data={
            'name': '開発チーム',
            'members': [],
            'is_admin': False,
            'department': sample_department.id,
            'permission_set_id': 1,
        })
        assert form.is_valid()


    # 部門の選択肢は会社名順、同じ会社の中では部門名順に並ぶこと
    def test_department_choices_are_ordered_by_company_name_then_name(self):
        company_b = Company.objects.create(name='B株式会社')
        company_a = Company.objects.create(name='A株式会社')
        Department.objects.create(company=company_b, name='A部')
        Department.objects.create(company=company_a, name='B部')
        Department.objects.create(company=company_a, name='A部')

        form = ManagementGroupForm()
        assert [(department.company.name, department.name) for department in form.fields['department'].queryset] == [
            ('A株式会社', 'A部'),
            ('A株式会社', 'B部'),
            ('B株式会社', 'A部'),
        ]

@pytest.fixture
def sample_department():
    company = Company.objects.create(name='サンプル株式会社')
    return Department.objects.create(company=company, name='開発部')
