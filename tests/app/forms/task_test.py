import pytest
from django.contrib.auth.models import User
from app.forms.task import TaskForm


@pytest.mark.django_db
class TestTaskForm:

    # 有効なデータでフォームが妥当と判定されること
    def test_valid_data_is_valid(self):
        form = TaskForm(data={
            'title': 'New Task',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })
        assert form.is_valid()

    # タイトル未入力の場合、フォームが無効と判定されること
    def test_missing_title_is_invalid(self):
        form = TaskForm(data={
            'title': '',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })
        assert not form.is_valid()
        assert 'title' in form.errors

    # 優先度が範囲外の場合、フォームが無効と判定されること
    def test_priority_out_of_range_is_invalid(self):
        form = TaskForm(data={
            'title': 'Task',
            'description': '',
            'status': 'todo',
            'priority': 6,
        })
        assert not form.is_valid()
        assert 'priority' in form.errors

    # 説明に#が含まれる場合は妥当と判定されること
    def test_description_with_hash_is_valid(self):
        form = TaskForm(data={
            'title': 'Task',
            'description': '関連Issue: #123',
            'status': 'todo',
            'priority': 3,
        })
        assert form.is_valid()

    # 説明に#が含まれない場合、フォームが無効と判定されること
    def test_description_without_hash_is_invalid(self):
        form = TaskForm(data={
            'title': 'Task',
            'description': 'Issue番号を含まない説明文',
            'status': 'todo',
            'priority': 3,
        })
        assert not form.is_valid()
        assert 'description' in form.errors

    # 担当者を指定した場合、cleaned_dataにUserインスタンスとして反映されること
    def test_cleaned_data_includes_assigned_to(self):
        user = User.objects.create_user(username='formuser', password='pass12345')
        form = TaskForm(data={
            'title': 'Assigned Task',
            'description': '',
            'status': 'todo',
            'priority': 3,
            'assigned_to': user.id,
        })
        assert form.is_valid()
        assert form.cleaned_data['assigned_to'] == user
