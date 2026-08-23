from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import Employee


# 社員を取得する(存在しなければ404)
def get_employee(*, pk: int) -> Employee:
    return get_object_or_404(Employee, pk=pk)


# 社員一覧を取得する(未評価のQuerySetを返す)
def list_employees() -> QuerySet[Employee]:
    return Employee.objects.with_user()
