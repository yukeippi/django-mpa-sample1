from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from app.lib.types import AuthenticatedHttpRequest
from app.forms import TaskForm, TaskStatusForm
from app.models import Task
from app.permissions.roles import can_delete_task, can_edit_task


# タスク一覧
@login_required
def index(request: AuthenticatedHttpRequest) -> HttpResponse:
    tasks_qs = Task.objects.all()
    paginator = Paginator(tasks_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/task/index.html', {
        'tasks': page_obj,
        'page_obj': page_obj,
    })


# タスク詳細
@login_required
def show(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'app/task/show.html', {
        'task': task,
        'can_edit': can_edit_task(request.user, task),
        'can_delete': can_delete_task(request.user, task),
        'status_form': TaskStatusForm(instance=task),
    })


# タスク詳細の右ペイン(一覧画面の行をクリックしたとき、htmxで中身だけを取得する)
@login_required
def pane(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'app/task/_detail_pane.html', {
        'task': task,
        'can_edit': can_edit_task(request.user, task),
        'can_delete': can_delete_task(request.user, task),
    })


# タスク新規作成
@login_required
def new(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == 'POST':
        return _create_task(request)
    return _display_new_form(request)


# タスク編集
@login_required
def edit(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    if not can_edit_task(request.user, task):
        raise PermissionDenied
    if request.method == 'POST':
        return _update_task(request, task)
    return _display_edit_form(request, task)


# タスクのステータス変更(詳細画面のモーダルから送信する。画面を持たないためPOSTのみ)
@login_required
@require_POST
def status(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    if not can_edit_task(request.user, task):
        raise PermissionDenied
    return _update_task_status(request, task)


# タスク削除
@login_required
def delete(request: AuthenticatedHttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    if not can_delete_task(request.user, task):
        raise PermissionDenied
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'タスクを削除しました。')
        return redirect('app:task_index')
    return render(request, 'app/task/delete.html', {'task': task})


# タスクAPI(E2Eテスト用)
@login_required
def api(request: AuthenticatedHttpRequest) -> HttpResponse:
    if request.method == 'GET':
        tasks = Task.objects.all().values('id', 'title', 'status', 'priority')
        return JsonResponse(list(tasks), safe=False)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 新規作成フォームを表示する
def _display_new_form(request):
    form = TaskForm()
    return _render_new_form(request, form)


# タスクの新規作成処理を行う
def _create_task(request):
    form = TaskForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    task = form.save(commit=False)
    task.created_by = request.user
    task.save()
    messages.success(request, 'タスクを作成しました。')
    return redirect('app:task_show', pk=task.pk)


# タスク新規作成フォームのレンダリング
def _render_new_form(request, form):
    return render(request, 'app/task/new.html', {'form': form})


# 編集フォームを表示する
def _display_edit_form(request, task):
    form = TaskForm(instance=task)
    return _render_edit_form(request, task, form)



# タスクの更新処理を行う
def _update_task(request, task):
    form = TaskForm(request.POST, instance=task)
    if not form.is_valid():
        return _render_edit_form(request, task, form)
    form.save()
    messages.success(request, 'タスクを更新しました。')
    return redirect('app:task_show', pk=task.pk)


# タスク編集フォームのレンダリング
def _render_edit_form(request, task, form):
    return render(request, 'app/task/edit.html', {'form': form, 'task': task})


# タスクのステータスを更新する(選択肢外の値は画面操作では送られないため、フォームを再表示せずエラーメッセージだけ出す)
def _update_task_status(request, task):
    form = TaskStatusForm(request.POST, instance=task)
    if not form.is_valid():
        messages.error(request, 'ステータスを変更できませんでした。')
        return redirect('app:task_show', pk=task.pk)
    form.save()
    messages.success(request, 'タスクを更新しました。')
    return redirect('app:task_show', pk=task.pk)
