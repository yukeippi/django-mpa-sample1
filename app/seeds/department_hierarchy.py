from app.models import Department, DepartmentHierarchy


# 部門の親子関係のシードデータを作成する
# サンプル株式会社を「本社 → 開発部・営業部 → 営業一課」の3階層にする。管理グループが効く範囲
# (主務部門の自分・親・兄弟。祖父母・子は対象外)を画面で確かめられるよう、兄弟と孫を含めている
def create() -> None:
    head_office = _get('本社')
    sales = _get('営業部')
    _create(department=head_office, parent_department=None)
    _create(department=_get('開発部'), parent_department=head_office)
    _create(department=sales, parent_department=head_office)
    _create(department=_get('営業一課'), parent_department=sales)


# サンプル株式会社の部門を名前で取得する
def _get(name):
    return Department.objects.get(company__name='サンプル株式会社', name=name)


# 親部門が同じ会社であることをfull_clean()で検証してから保存する(save()は検証を行わないため)
def _create(*, department, parent_department):
    hierarchy = DepartmentHierarchy(department=department, parent_department=parent_department)
    hierarchy.full_clean()
    hierarchy.save()
