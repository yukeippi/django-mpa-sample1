from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import Task


# タスクを取得する(存在しなければ404)
def get_task(*, pk: int) -> Task:
    return get_object_or_404(Task, pk=pk)


# タスク一覧を取得する(未評価のQuerySetを返す)
def list_tasks() -> QuerySet[Task]:
    return Task.objects.all()
