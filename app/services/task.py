from django.contrib.auth.models import User
from app.forms.task import TaskForm
from app.models import Task


# タスクを作成する
def create(*, form: TaskForm, created_by: User) -> Task:
    return Task.objects.create(created_by=created_by, **form.cleaned_data)


# タスクを更新する
def update(*, task: Task, form: TaskForm) -> Task:
    for field, value in form.cleaned_data.items():
        setattr(task, field, value)
    task.save(update_fields=[*form.cleaned_data.keys()])
    return task


# タスクを削除する
def delete(*, task: Task) -> None:
    task.delete()
