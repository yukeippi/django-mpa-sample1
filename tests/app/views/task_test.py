import pytest
from app.models import Task


@pytest.mark.django_db
class TestTaskIndexView:

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_index_requires_login(self, client):
        response = client.get('/tasks/')
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # タスクが無い場合、空の一覧が返ること
    def test_index_with_no_tasks(self, auth_client):
        response = auth_client.get('/tasks/')
        assert response.status_code == 200
        assert list(response.context['tasks']) == []

    # タスクが一覧に表示されること
    def test_index_with_tasks(self, auth_client):
        Task.objects.create(title='Task 1')
        Task.objects.create(title='Task 2')

        response = auth_client.get('/tasks/')
        assert response.status_code == 200
        assert len(response.context['tasks']) == 2


@pytest.mark.django_db
class TestTaskShowView:

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_show_requires_login(self, client):
        task = Task.objects.create(title='Task Detail')
        response = client.get(f'/tasks/{task.id}/')
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # 存在するタスクの詳細が取得できること
    def test_show_existing_task(self, auth_client):
        task = Task.objects.create(title='Task Detail')

        response = auth_client.get(f'/tasks/{task.id}/')
        assert response.status_code == 200
        assert response.context['task'] == task

    # 存在しないタスクの場合404が返ること
    def test_show_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.get('/tasks/9999/')
        assert response.status_code == 404

    # 誰のタスクでも一覧・詳細は閲覧できる(閲覧に所有者制限は無い)こと
    def test_show_task_owned_by_other_user(self, auth_client, other_user):
        task = Task.objects.create(title='Other User Task', created_by=other_user)

        response = auth_client.get(f'/tasks/{task.id}/')
        assert response.status_code == 200

    # 編集権限のあるユーザーには、ステータスの「変更」ボタンとモーダルが表示されること
    def test_show_by_editor_displays_status_change_button_and_modal(self, auth_client, sample_user):
        task = Task.objects.create(title='Task Detail', created_by=sample_user)

        response = auth_client.get(f'/tasks/{task.id}/')

        assert 'id="change-status-button"' in response.content.decode()
        assert 'id="task-status-modal"' in response.content.decode()

    # 編集権限の無いユーザーには、ステータスの「変更」ボタンもモーダルも表示されないこと
    def test_show_by_unrelated_user_hides_status_change_button_and_modal(self, other_auth_client, sample_user):
        task = Task.objects.create(title='Task Detail', created_by=sample_user)

        response = other_auth_client.get(f'/tasks/{task.id}/')

        assert 'id="change-status-button"' not in response.content.decode()
        assert 'id="task-status-modal"' not in response.content.decode()

    # ステータス変更モーダルのセレクトでは、現在のステータスが選択されていること
    def test_show_status_modal_selects_current_status(self, auth_client, sample_user):
        task = Task.objects.create(title='Task Detail', status='in_progress', created_by=sample_user)

        response = auth_client.get(f'/tasks/{task.id}/')

        assert '<option value="in_progress" selected>' in response.content.decode()


@pytest.mark.django_db
class TestTaskCreateView:

    # GETリクエストでフォームが表示されること
    def test_get_returns_form(self, auth_client):
        response = auth_client.get('/tasks/new/')
        assert response.status_code == 200
        assert 'form' in response.context

    # 有効なデータでPOSTするとタスクが作成され詳細ページにリダイレクトされること
    def test_post_valid_data_creates_task_and_redirects(self, auth_client):
        response = auth_client.post('/tasks/new/', {
            'title': 'Client Created Task',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task = Task.objects.get(title='Client Created Task')
        assert response.status_code == 302
        assert response.url == f'/tasks/{task.id}/'

    # 作成者(created_by)がログインユーザーとして自動設定されること
    def test_post_valid_data_sets_created_by(self, auth_client, sample_user):
        auth_client.post('/tasks/new/', {
            'title': 'Task With Creator',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task = Task.objects.get(title='Task With Creator')
        assert task.created_by == sample_user

    # 無効なデータでPOSTするとフォームが再表示されること
    def test_post_invalid_data_redisplays_form(self, auth_client):
        response = auth_client.post('/tasks/new/', {
            'title': '',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        assert response.status_code == 200
        assert response.context['form'].is_valid() is False


@pytest.mark.django_db
class TestTaskEditView:

    # GETリクエストで既存タスクの値がフォームの初期値に入っていること
    def test_get_returns_form_with_initial_values(self, auth_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = auth_client.get(f'/tasks/{task.id}/edit/')
        assert response.status_code == 200
        assert response.context['form'].initial['title'] == task.title

    # 有効なデータでPOSTするとタスクが更新され詳細ページにリダイレクトされること
    def test_post_valid_data_updates_task_and_redirects(self, auth_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/edit/', {
            'title': 'Updated Title',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task.refresh_from_db()
        assert task.title == 'Updated Title'
        assert response.status_code == 302
        assert response.url == f'/tasks/{task.id}/'

    # 存在しないタスクの場合404が返ること
    def test_edit_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.get('/tasks/9999/edit/')
        assert response.status_code == 404

    # 無効なデータでPOSTするとフォームが再表示されること
    def test_post_invalid_data_redisplays_form(self, auth_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/edit/', {
            'title': '',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        assert response.status_code == 200
        assert response.context['form'].is_valid() is False

        task.refresh_from_db()
        assert task.title == 'Original Title'

    # 作成者でも担当者でもない一般ユーザーが編集しようとすると403が返ること
    def test_edit_by_unrelated_user_returns_403(self, other_auth_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = other_auth_client.get(f'/tasks/{task.id}/edit/')
        assert response.status_code == 403

    # 作成者でも担当者でもない一般ユーザーがPOSTで更新しようとすると403が返り、タスクが変更されないこと
    def test_edit_by_unrelated_user_post_returns_403(self, other_auth_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = other_auth_client.post(f'/tasks/{task.id}/edit/', {
            'title': 'Hacked Title',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task.refresh_from_db()
        assert response.status_code == 403
        assert task.title == 'Original Title'

    # 担当者は編集できること
    def test_edit_by_assigned_user_succeeds(self, other_auth_client, sample_user, other_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user, assigned_to=other_user)

        response = other_auth_client.get(f'/tasks/{task.id}/edit/')
        assert response.status_code == 200

    # 担当者はPOSTで更新を完了できること
    def test_edit_by_assigned_user_can_update(self, other_auth_client, sample_user, other_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user, assigned_to=other_user)

        response = other_auth_client.post(f'/tasks/{task.id}/edit/', {
            'title': 'Updated By Assignee',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task.refresh_from_db()
        assert response.status_code == 302
        assert task.title == 'Updated By Assignee'

    # 管理者は誰のタスクでも編集できること
    def test_edit_by_admin_succeeds(self, admin_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = admin_client.get(f'/tasks/{task.id}/edit/')
        assert response.status_code == 200

    # 管理者はPOSTで誰のタスクでも更新を完了できること
    def test_edit_by_admin_can_update(self, admin_client, sample_user):
        task = Task.objects.create(title='Original Title', created_by=sample_user)

        response = admin_client.post(f'/tasks/{task.id}/edit/', {
            'title': 'Updated By Admin',
            'description': '',
            'status': 'todo',
            'priority': 3,
        })

        task.refresh_from_db()
        assert response.status_code == 302
        assert task.title == 'Updated By Admin'


@pytest.mark.django_db
class TestTaskDeleteView:

    # GETリクエストで削除確認ページが表示されること
    def test_get_returns_confirmation_page(self, auth_client, sample_user):
        task = Task.objects.create(title='To Delete', created_by=sample_user)

        response = auth_client.get(f'/tasks/{task.id}/delete/')
        assert response.status_code == 200
        assert response.context['task'] == task

    # POSTするとタスクが削除され一覧ページにリダイレクトされること
    def test_post_deletes_task_and_redirects_to_index(self, auth_client, sample_user):
        task = Task.objects.create(title='To Delete', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/delete/')

        assert response.status_code == 302
        assert response.url == '/tasks/'
        assert Task.objects.filter(id=task.id).count() == 0

    # 存在しないタスクの場合404が返ること
    def test_delete_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.get('/tasks/9999/delete/')
        assert response.status_code == 404

    # 作成者でも担当者でもない一般ユーザーが削除しようとすると403が返り、タスクが削除されないこと
    def test_delete_by_unrelated_user_returns_403(self, other_auth_client, sample_user):
        task = Task.objects.create(title='Protected Task', created_by=sample_user)

        response = other_auth_client.post(f'/tasks/{task.id}/delete/')

        assert response.status_code == 403
        assert Task.objects.filter(id=task.id).count() == 1


@pytest.mark.django_db
class TestTaskStatusView:

    # 編集権限のあるユーザーはステータスを変更でき、詳細ページにリダイレクトされること
    def test_post_by_creator_updates_status_and_redirects(self, auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/status/', {'status': 'in_progress'})

        task.refresh_from_db()
        assert response.status_code == 302
        assert response.url == f'/tasks/{task.id}/'
        assert task.status == 'in_progress'

    # ステータスを変更すると「タスクを更新しました。」と表示されること
    def test_post_by_creator_shows_success_message(self, auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/status/', {'status': 'done'}, follow=True)

        assert 'タスクを更新しました。' in [str(message) for message in response.context['messages']]

    # 担当者はステータスを変更できること
    def test_post_by_assigned_user_updates_status(self, other_auth_client, sample_user, other_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user, assigned_to=other_user)

        other_auth_client.post(f'/tasks/{task.id}/status/', {'status': 'done'})

        task.refresh_from_db()
        assert task.status == 'done'

    # 管理者は誰のタスクでもステータスを変更できること
    def test_post_by_admin_updates_status(self, admin_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        admin_client.post(f'/tasks/{task.id}/status/', {'status': 'done'})

        task.refresh_from_db()
        assert task.status == 'done'

    # ステータス以外の項目は変わらないこと
    def test_post_does_not_change_other_fields(self, auth_client, sample_user):
        task = Task.objects.create(
            title='Task', description='説明 #1', status='todo', priority=2, created_by=sample_user,
        )

        auth_client.post(f'/tasks/{task.id}/status/', {
            'status': 'done', 'title': 'Changed', 'description': 'Changed #2', 'priority': 5,
        })

        task.refresh_from_db()
        assert task.title == 'Task'
        assert task.description == '説明 #1'
        assert task.priority == 2

    # 選択肢に無い値を送った場合、ステータスは変更されず詳細ページにリダイレクトされること
    def test_post_invalid_status_does_not_update_and_redirects(self, auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/status/', {'status': 'unknown'})

        task.refresh_from_db()
        assert response.status_code == 302
        assert response.url == f'/tasks/{task.id}/'
        assert task.status == 'todo'

    # 選択肢に無い値を送った場合、エラーメッセージが表示されること
    def test_post_invalid_status_shows_error_message(self, auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = auth_client.post(f'/tasks/{task.id}/status/', {'status': 'unknown'}, follow=True)

        assert 'ステータスを変更できませんでした。' in [str(message) for message in response.context['messages']]

    # 編集権限の無いユーザーが変更しようとすると403が返り、ステータスは変わらないこと
    def test_post_by_unrelated_user_returns_403(self, other_auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = other_auth_client.post(f'/tasks/{task.id}/status/', {'status': 'done'})

        task.refresh_from_db()
        assert response.status_code == 403
        assert task.status == 'todo'

    # 存在しないタスクの場合404が返ること
    def test_post_nonexistent_task_returns_404(self, auth_client):
        response = auth_client.post('/tasks/9999/status/', {'status': 'done'})

        assert response.status_code == 404

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_post_requires_login(self, client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = client.post(f'/tasks/{task.id}/status/', {'status': 'done'})

        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # GETでアクセスした場合は405が返ること(画面を持たない)
    def test_get_returns_405(self, auth_client, sample_user):
        task = Task.objects.create(title='Task', status='todo', created_by=sample_user)

        response = auth_client.get(f'/tasks/{task.id}/status/')

        assert response.status_code == 405


@pytest.mark.django_db
class TestTaskApiView:

    # 未ログインの場合、ログインページにリダイレクトされること
    def test_api_requires_login(self, client):
        response = client.get('/api/tasks/')
        assert response.status_code == 302
        assert response.url.startswith('/login/')

    # タスクが無い場合、空配列がJSONで返ること
    def test_api_returns_empty_list(self, auth_client):
        response = auth_client.get('/api/tasks/')

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'
        assert response.json() == []

    # タスクの内容が正しい形式・値でJSON化されること
    def test_api_returns_task_data(self, auth_client):
        task = Task.objects.create(title='API Task', status='todo', priority=3)

        response = auth_client.get('/api/tasks/')
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert data[0] == {
            'id': task.id,
            'title': 'API Task',
            'status': 'todo',
            'priority': 3,
        }

    # 複数タスクがすべて含まれること
    def test_api_returns_multiple_tasks(self, auth_client):
        Task.objects.create(title='Task 1', status='todo', priority=1)
        Task.objects.create(title='Task 2', status='done', priority=2)

        response = auth_client.get('/api/tasks/')

        assert response.status_code == 200
        assert len(response.json()) == 2

    # GET以外のメソッドは405が返ること
    def test_api_post_returns_405(self, auth_client):
        response = auth_client.post('/api/tasks/')

        assert response.status_code == 405
        assert response.json() == {'error': 'Method not allowed'}
