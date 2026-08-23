from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import Company


# 会社を取得する(存在しなければ404)
def get_company(*, pk: int) -> Company:
    return get_object_or_404(Company, pk=pk)


# 会社一覧を取得する(未評価のQuerySetを返す)
def list_companies() -> QuerySet[Company]:
    return Company.objects.all()
