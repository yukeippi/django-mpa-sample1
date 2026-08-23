from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import ManagementGroup


# 管理グループを取得する(存在しなければ404)
def get_management_group(*, pk: int) -> ManagementGroup:
    return get_object_or_404(ManagementGroup, pk=pk)


# 管理グループ一覧を取得する(未評価のQuerySetを返す)
def list_management_groups() -> QuerySet[ManagementGroup]:
    return ManagementGroup.objects.all()
