import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from app.models import Task


# Taskモデルのテストクラス
@pytest.mark.django_db
class TestTaskModel:

    # 最小限のフィールドでタスクを作成できること
    def test_create_task_with_minimal_fields(self):
        task = Task.objects.create(title='Test Task')

        assert task.id is not None
        assert task.title == 'Test Task'
        assert task.description == ''
        assert task.status == 'todo'
        assert task.priority == 3
        assert task.assigned_to is None

    # 全フィールドを指定してタスクを作成できること
    def test_create_task_with_all_fields(self, sample_user):
        due_date = date.today() + timedelta(days=7)
        task = Task.objects.create(
            title='Complete Task',
            description='This is a test task #1',
            status='in_progress',
            priority=1,
            assigned_to=sample_user,
            due_date=due_date
        )

        assert task.title == 'Complete Task'
        assert task.description == 'This is a test task #1'
        assert task.status == 'in_progress'
        assert task.priority == 1
        assert task.assigned_to == sample_user
        assert task.due_date == due_date

    # __str__メソッドがタイトルを返すこと
    def test_task_str_method(self):
        task = Task.objects.create(title='String Test Task')
        assert str(task) == 'String Test Task'

    # タスクが作成日時の降順でソートされること
    def test_task_ordering(self):
        task1 = Task.objects.create(title='First Task')
        task2 = Task.objects.create(title='Second Task')
        task3 = Task.objects.create(title='Third Task')

        tasks = list(Task.objects.all())
        assert tasks[0] == task3
        assert tasks[1] == task2
        assert tasks[2] == task1





    # 優先度が1-5の範囲外の場合、full_clean()でpriorityのエラーになること
    @pytest.mark.parametrize('priority', [0, 6])
    def test_full_clean_rejects_priority_out_of_range(self, priority):
        task = Task(title='Task', priority=priority)
        with pytest.raises(ValidationError) as error:
            task.full_clean()
        assert 'priority' in error.value.error_dict

    # 説明の形式違反はfull_clean()でdescriptionのエラーになること(形式のパターン網羅はvalidators_test.pyで行う)
    def test_full_clean_rejects_description_without_issue_reference(self):
        task = Task(title='Task', description='Issue番号を含まない説明文')
        with pytest.raises(ValidationError) as error:
            task.full_clean()
        assert 'description' in error.value.error_dict

    # 優先度が1-5の範囲外の場合はエラーになること(DB制約)
    def test_priority_must_be_in_valid_range(self):
        with pytest.raises(IntegrityError):
            Task.objects.create(title='Invalid Priority Task', priority=6)

    # タスクとユーザーの関連が正しく機能すること
    def test_task_user_relationship(self, sample_user):
        task1 = Task.objects.create(title='Task 1', assigned_to=sample_user)
        task2 = Task.objects.create(title='Task 2', assigned_to=sample_user)

        user_tasks = sample_user.tasks.all()
        assert task1 in user_tasks
        assert task2 in user_tasks
        assert user_tasks.count() == 2

    # ユーザーが削除されてもタスクは削除されず、assigned_toがNullになること
    def test_task_user_deletion_sets_null(self, sample_user):
        task = Task.objects.create(title='Task', assigned_to=sample_user)
        sample_user.delete()

        task.refresh_from_db()
        assert task.assigned_to is None
        assert task.id is not None

    # 期限が過去の場合、is_overdue()がTrueを返すこと
    def test_is_overdue_with_past_due_date(self):
        past_date = date.today() - timedelta(days=1)
        task = Task.objects.create(
            title='Overdue Task',
            due_date=past_date,
            status='in_progress'
        )
        assert task.is_overdue() is True

    # 期限が未来の場合、is_overdue()がFalseを返すこと
    def test_is_overdue_with_future_due_date(self):
        future_date = date.today() + timedelta(days=1)
        task = Task.objects.create(
            title='Future Task',
            due_date=future_date
        )
        assert task.is_overdue() is False

    # 期限が設定されていない場合、is_overdue()がFalseを返すこと
    def test_is_overdue_with_no_due_date(self):
        task = Task.objects.create(title='No Due Date Task')
        assert task.is_overdue() is False

    # 完了したタスクは期限を過ぎていてもis_overdue()がFalseを返すこと
    def test_is_overdue_completed_task(self):
        past_date = date.today() - timedelta(days=1)
        task = Task.objects.create(
            title='Completed Task',
            due_date=past_date,
            status='done'
        )
        assert task.is_overdue() is False

    # todoステータスのタスクは完了可能であること
    def test_can_be_completed_todo_status(self):
        task = Task.objects.create(title='Todo Task', status='todo')
        assert task.can_be_completed() is True

    # in_progressステータスのタスクは完了可能であること
    def test_can_be_completed_in_progress_status(self):
        task = Task.objects.create(title='In Progress Task', status='in_progress')
        assert task.can_be_completed() is True

    # doneステータスのタスクは完了不可であること
    def test_can_be_completed_done_status(self):
        task = Task.objects.create(title='Done Task', status='done')
        assert task.can_be_completed() is False
