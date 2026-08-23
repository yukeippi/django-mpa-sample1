from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import Department


# 部門を取得する(存在しなければ404)
def get_department(*, pk: int) -> Department:
    return get_object_or_404(Department, pk=pk)


# 部門一覧を取得する(未評価のQuerySetを返す)
def list_departments() -> QuerySet[Department]:
    return Department.objects.with_company()
