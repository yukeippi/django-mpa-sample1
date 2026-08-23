# Django Development Guidelines

> **このファイルの位置づけ**: 別のDjangoプロジェクトにそのままコピーして使う、再利用可能な開発規約集(`CLAUDE.md`が「雛形として引き継ぐ」と定義している章の一つ)。書く内容は「このプロジェクトの現在の状態」ではなく、Djangoプロジェクト一般に適用できる規約・パターンにすること。
>
> - 各ルールの例に出てくる`Task`/`Employee`等のモデル名は、あくまでパターンを説明するための例示。実際のこのプロジェクトのモデル・ファイル構成と完全に一致している必要はない(コピー先の別プロジェクトではどのみち別のモデル名になる)
> - 一方、規約・パターンの説明自体に矛盾や誤りがある場合は、コピー先でも同じ混乱を招くため修正する

## File Structure Rules

models、forms、views、services、selectors、validators、tests、templatesはディレクトリ化し、機能ごとにファイル分割してください。検証ロジックがForm/Validator/Service/DB制約のどこに属するかはValidation Rulesを参照。

### Examples
- models/todo.py
- views/todo.py
- services/todo.py
- selectors/todo.py
- validators/todo.py
- errors/todo.py
- messages/todo.py
- tests/unit/models/todo_test.py
- tests/unit/forms/todo_test.py
- tests/unit/views/todo_test.py
- tests/unit/services/todo_test.py
- tests/unit/selectors/todo_test.py
- tests/unit/validators/todo_test.py
- tests/e2e/todo_test.py

各ディレクトリに__init__.pyを配置すること。

`tests/unit/`配下は、ソース側の`models/`, `forms/`, `views/`, `services/`, `selectors/`, `validators/`, `lib/`と対応するレイヤーごとのディレクトリにさらに分割する(Railsの`test/models/`, `test/controllers/`に相当)。`app/lib/`(`auth.py`/`permissions.py`等、app内で共有するロジック。詳細はCommon Module Rulesを参照)のテストも同様に`tests/unit/lib/`に置く(例: `tests/unit/lib/auth_test.py`)。`app/errors/`・`app/messages/`・`app/rules/`(役割はError Rules/Message Rules/Rules Directory Rulesを参照)は単純な対応表であることが多く、分岐ロジックが生じた場合のみ`tests/unit/errors/`・`tests/unit/messages/`を追加する。`tests/e2e/`はページ単位のテストのため、このレイヤー分割は行わない。

## Layout Rules

もっとも低レイヤーの共通テンプレート(全ページの土台となるレイアウト)は `templates/layouts/` ディレクトリに置く。既定のレイアウトファイル名は `default.html` とする。将来的に別のレイアウトが必要になった場合は `layouts/admin.html` のように用途名を付けたファイルを追加する。

レイアウト本体はHTMLの骨格(`<head>`の共通アセット読み込みと`{% block %}`)だけにとどめ、極力コンパクトに保つ。ナビゲーションバーやフラッシュメッセージ表示のような、ページ間で共通だが内容として独立した部品は、レイアウトに直書きせず `app/templates/common/` 配下のパーシャル(`_navbar.html`, `_messages.html` など)に切り出し、レイアウトから `{% include %}` で読み込む(置き場所の考え方は下記Common Module Rulesを参照)。

### Example

```
app/templates/layouts/
└── default.html       # 骨格のみ。{% include %}で各パーシャルを読み込む

app/templates/common/
├── _navbar.html        # ナビゲーションバー
└── _messages.html      # フラッシュメッセージ表示
```

```html
<!-- layouts/default.html -->
<body>
    {% include 'common/_navbar.html' %}
    <div class="container">
        {% include 'common/_messages.html' %}
        {% block content %}{% endblock %}
    </div>
</body>
```

## Template Rules

テンプレートの継承は3段階にする。各ページ側は`{% block %}`の中身だけを記述する最小限の内容にする。

1. `layouts/default.html`: サイト全体の骨格(`<head>`の共通アセット読み込みと`{% block %}`定義)。詳細はLayout Rulesを参照
2. `app/<model>/base.html`: モデル単位の中間テンプレート。`layouts/default.html`を継承し、そのモデルの全ページで共通の`{% block %}`(モデル別CSSの読み込み等)をここで埋める。詳細はCSS Rulesを参照
3. `app/<model>/<page>.html`: ページごとのテンプレート。`app/<model>/base.html`を継承し、`title`/`content`など、そのページ固有の`{% block %}`だけを埋める

### Example

```html
<!-- app/article/base.html -->
{% extends 'layouts/default.html' %}
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'app/article.css' %}">
{% endblock %}
```

```html
<!-- app/article/index.html -->
{% extends 'app/article/base.html' %}

{% block title %}記事一覧{% endblock %}

{% block content %}
<div class="container mt-5">
  <div class="d-flex justify-content-between align-items-center mb-4">
    <h1 class="mb-0">記事一覧</h1>
    <a href="{% url 'app:article_create' %}" class="btn btn-success">新規作成</a>
  </div>

  {% if articles %}
    <div class="list-group">
      {% for article in articles %}
        <a href="{% url 'app:article_detail' article.pk %}" class="list-group-item list-group-item-action">
          <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1">{{ article.title }}</h5>
            <small class="text-muted">{{ article.created_at|date:"Y/m/d H:i" }}</small>
          </div>
          <p class="mb-1">{{ article.content|truncatewords:30 }}</p>
          <small class="text-muted">投稿者: {{ article.user.username }}</small>
        </a>
      {% endfor %}
    </div>
  {% else %}
    <div class="alert alert-info" role="alert">
      記事がまだありません。
    </div>
  {% endif %}
</div>
{% endblock %}
```

CSSフレームワークの採用は問わない(プロジェクトごとに選定する)。上記例のBootstrapクラスはあくまで一例。

## Template Directory Rules

テンプレートが増えても1つのディレクトリに大量にファイルが並んで名前が衝突しないよう、Railsのようにモデルごとにディレクトリを切り、決められたファイル名で管理する。

- `index.html`: 一覧
- `show.html`: 詳細
- `new.html`: 新規作成フォーム
- `edit.html`: 編集フォーム

### Example

```
templates/app/task/index.html
templates/app/task/show.html
templates/app/task/new.html
templates/app/task/edit.html
```

## View Naming Rules

ビューは関数ベースビュー(FBV)で実装する。関数名・テンプレートファイル名・URL名の3つの対応が一目でわかるよう、以下のルールで揃える。

- **関数名**: テンプレートファイル名(上記Template Directory Rulesの`index`/`show`/`new`/`edit`)と同じ名前にする。削除確認ページを伴う場合は`delete`とする。
- **URL名**: `<モデル名>_<関数名>` とする(例: `task_index`, `task_show`, `task_new`, `task_edit`, `task_delete`)。同一Djangoアプリ内で複数モデルのURL名が衝突しないようにするため。
- **関数の配置**: `app/views/<model>.py` に関数として定義する。複数モデルの関数名(`index`/`show`等)が衝突するため、`app/views/__init__.py` では個々の関数をフラットに再エクスポートせず、モジュール単位でインポートする。`urls.py`側は `views.<model>.<関数名>` の形で参照する。

### Example

```python
# app/views/__init__.py
from . import home
from . import task

__all__ = ['home', 'task']
```

```python
# app/views/task.py
def index(request):
    ...

def show(request, pk):
    ...
```

```python
# app/urls.py
from . import views

urlpatterns = [
    path('tasks/', views.task.index, name='task_index'),
    path('tasks/<int:pk>/', views.task.show, name='task_show'),
    path('tasks/new/', views.task.new, name='task_new'),
    path('tasks/<int:pk>/edit/', views.task.edit, name='task_edit'),
    path('tasks/<int:pk>/delete/', views.task.delete, name='task_delete'),
]
```

## View Method-Branch Rules

CBVを使わずFBVを選んでいるのは、Railsのコントローラーのように「1つの関数の中で自分がすべて制御している」明示性を保つため。ただし`request.method`でGET/POSTを分岐する関数が肥大化しやすいので、以下のルールで整理する。

- **分岐関数は振り分けだけにする**: `new`/`edit`のようにGET/POSTで処理が変わる関数は、分岐と委譲だけを行う薄い実装にする。実際の処理はprivateヘルパー関数(`_`始まり)に切り出す。
- **ヘルパー名は処理内容で付ける**: `_edit_get`/`_edit_post`のようにHTTPメソッド名をそのまま使う命名は避ける。中身を見なくても分岐関数を読むだけで何をしているか分かるよう、`_display_edit_form`/`_update_task`のように行う処理そのもので名付ける。
- **ファイル内の並び順**: モデルの公開アクション(`index`/`show`/`new`/`edit`/`delete`など)をファイル上部にまとめて書き、ファイル全体を見ればそのビューが持つアクション一覧が把握できるようにする。その下に区切りコメントを置き、privateヘルパーをまとめて配置する。

### Example

```python
# app/views/task.py

# タスク編集
def edit(request, pk):
    task = selectors.task.get_task_for_edit(task_id=pk, user=request.user)  # Viewは直接ORMを呼ばない(Selector Rules参照)
    if request.method == 'POST':
        return _update_task(request, task)
    return _display_edit_form(request, task)


# (他の公開アクションが続く)


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 編集フォームを表示する
def _display_edit_form(request, task):
    form = TaskForm(initial=_task_initial(task))
    return _render_edit_form(request, task, form)


# タスクの更新処理を行う
def _update_task(request, task):
    form = TaskForm(request.POST)
    if not form.is_valid():
        return _render_edit_form(request, task, form)
    services.task.update(task=task, form=form)
    messages.success(request, 'タスクを更新しました。')
    return redirect('app:task_show', pk=task.pk)


# instanceの現在値からFormの初期値を組み立てる(ModelFormを使わないため明示的に行う)
def _task_initial(task):
    return {'title': task.title, 'description': task.description, 'status': task.status}


# タスク編集フォームのレンダリング
def _render_edit_form(request, task, form):
    return render(request, 'app/task/edit.html', {'form': form, 'task': task})
```

privateヘルパーは、フォームの束縛・serviceの呼び出し・messages・リダイレクトのみを行う。モデルへの書き込みはヘルパー内に書かず、必ず`app/services/`の関数を呼ぶ(Service Rules参照)。

更新系のPOSTは、成功時に必ずリダイレクトする(POST-Redirect-GET)。ブラウザの再送信を防ぎ、「GETは表示・POSTは更新」の境界を保つため。

## Control Flow Rules

`if`のネストを深くしない。条件が成立しない場合や異常系は早期に`return`し、`else`で包まずインデントを1段に保つ(ガード節/早期return)。ビューに限らず、モデル・フォーム・service・共有モジュールなど全てのPythonコードに適用する。

### Example

```python
# 避ける書き方(ネストが深い)
def _create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = services.task.create(form=form)
            messages.success(request, 'タスクを作成しました。')
            return redirect('app:task_show', pk=task.pk)
        else:
            return _render_new_form(request, form)
    else:
        return _render_new_form(request, TaskForm())

# 良い書き方(早期returnでネストを浅く保つ)
def _create_task(request):
    form = TaskForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    task = services.task.create(form=form)
    messages.success(request, 'タスクを作成しました。')
    return redirect('app:task_show', pk=task.pk)
```

## Function Signature Rules

関数・メソッドのシグネチャは、実際の利用実態を正確に表すものにする。ビューに限らず、モデル・フォーム・service・共有モジュールなど全てのPythonコードに適用する。

- **使わない引数は持たない**: 関数内で参照していない引数は削除する。シグネチャに残しておくと「この値が結果に影響する」という誤った契約を呼び出し側に示してしまい、渡した値が実際の処理と食い違っていても検出されない。他の関数とシグネチャを揃えたいという理由だけで意味のない引数を残さない
- **公開関数の引数と戻り値には型注釈(type hints)を付ける**: 呼び出し側との契約を明示し、IDEの補完・型チェッカーの恩恵を受けられるようにするため。以下は対象外とする
  - 同一ファイル内で完結する実装詳細であるprivateヘルパー(`_`始まり)
  - `clean()`/`save()`/`__str__()`/`__init__()`のような、基底クラス・Python自身がシグネチャを決めるメソッド。`-> None`や`*args, **kwargs`を書き足しても実際の情報が増えないため

### Example

```python
# 避ける書き方(引数のcompanyは使わず、form.cleaned_data内のIDから別途取得し直している)
def update(company, form) -> Company:
    company = Company.objects.get(pk=form.cleaned_data['company_id'])
    company.name = form.cleaned_data['name']
    company.save(update_fields=['name'])
    return company

# 良い書き方(実際に使う引数だけを、型注釈付きで受け取る)
def update(*, company: Company, form: CompanyForm) -> Company:
    company.name = form.cleaned_data['name']
    company.save(update_fields=['name'])
    return company
```

## Partial Template Rules

Djangoにはpartialに関するネーミング規則が無いため、Railsに倣い、`{% include %}` で読み込むパーシャルテンプレートのファイル名の先頭には `_` を付ける。

### Example

```
templates/app/task/_form.html
templates/app/task/_task_card.html
```

## Comment Rules

関数・メソッド・クラスの説明にはdocstringを使わず、定義の上に通常のコメントで記述する。

### Example

```python
# タスク管理のためのモデル
class Task(models.Model):

    # 期限を過ぎているかチェック
    def is_overdue(self):
        ...
```

## CSS Rules

CSSは「共通ファイル」と「モデルごとのファイル」に分ける。モデルごとのファイルは、そのモデルのindex/show/new/editページで共通のファイルを1つ使う(ページ単位には分けない)。

自前で書くCSSは(共通・モデル別を問わず)全てDjangoアプリの`app/static/app/`に置く。トップレベルの`static/`は、Bootstrap等サードパーティ製のvendorファイル専用とする(自前のCSSと混在させない)。

### ディレクトリ構成

```
static/
└── vendor/            # サードパーティ製ファイル(Bootstrap等)専用
    └── bootstrap/...
app/static/app/
├── common.css          # 全ページ共通のスタイル(自前CSSはここに置く)
└── task.css            # taskモデル関連ページ(index/show/new/edit)共通のスタイル
```

### 読み込み方法

`layouts/default.html` で `app/common.css` を常に読み込む。モデル別CSSは、`index`/`show`/`new`/`edit`/`delete`の各ページが個別に`{% block extra_css %}`を書くと重複するため、Template Rulesの`app/<model>/base.html`(モデル単位の中間テンプレート)の`extra_css`ブロックにまとめる。`_form.html`のような`{% include %}`用パーシャルとは役割が違うため、`base.html`に`_`は付けない。

```html
<!-- layouts/default.html -->
<link rel="stylesheet" href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}">
<link rel="stylesheet" href="{% static 'app/common.css' %}">
{% block extra_css %}{% endblock %}
```

## Common Module Rules

共有モジュールは、共有する範囲によって置き場所を分ける。Pythonモジュールに限らず、テンプレートも同じ考え方で置き場所を分ける。

`app/lib/`は、`models/`/`views/`/`forms/`/`services/`のいずれにも属さない補助的なコードの置き場である。業務ロジック(モデルへの書き込みを伴う処理)は`app/lib/`ではなく`app/services/`に置く(Service Rules参照)。serviceは補助的な共有コードではなく、`models/`/`views/`/`forms/`と同列の層として扱う。

- **1つのアプリ内で共有**: `app/lib/` に置く(Railsの`lib/`相当)。`urls.py`/`apps.py`/`admin.py`のような、Djangoの規約でアプリ直下に置くと決まっているファイルはそのままアプリ直下に残し、開発者が追加した「app内で共有するロジック」だけを`app/lib/`にまとめる。役割ごとにファイルを分ける: 認証(ログイン等、誰であるかの検証)は`app/lib/auth.py`、汎用ユーティリティは`app/lib/utils.py`(増えてきたら`app/lib/utils/`ディレクトリ化し、関心事ごとにファイル分割する。例: `utils/date.py`)。ナビゲーションバー・フラッシュメッセージ表示のような特定のモデルに属さないパーシャルテンプレート(`app/templates/common/`)も同じ考え方で、このアプリ専用の置き場に置く。「複数アプリ間で共有」に見えても、実際に共有先の別アプリが存在しない限りは、このアプリ内に留める。バリデーション(Pure Function)や権限判定は補助的な共有コードではなく`app/validators/`・`app/permissions/`という同列の層として最初から扱う(Validator Rules参照)。
  - 例外: `app/management/commands/`(Djangoがこの場所を前提にコマンドを自動検出する)と`app/seeds/`(Seed Data Rules参照、モデルごとのデータ生成スクリプト群という別カテゴリ)は`app/lib/`に含めない。
  - **`app/lib/`配下のモジュールが肥大化した場合の昇格**: 関心事が独立したサブシステムと呼べる規模になった場合、`app/permissions/`のように`models/`/`views/`/`forms/`/`services/`等と同列のトップレベルディレクトリへ昇格してよい。昇格後は他のトップレベルディレクトリと同じ構成規則(ディレクトリ化・`__init__.py`配置・テストディレクトリの対応)に従う。
- **複数アプリ間で共有**: `app/` と同列に共有専用アプリ `common/` を作り、`INSTALLED_APPS` に登録して置く。これは実際に2つ以上のアプリから使われるようになった時点で行う。

#### 判断に迷った場合

`app/lib/` に置くべきか `app/services/` に置くべきか迷ったら、次で判断する。

- モデルへの書き込みを行う、またはトランザクションを必要とする → `app/services/`
- 値の計算・変換・判定のみで、DBを変更しない → `app/lib/`

```
config/
app/
├── urls.py                  # Djangoの規約でアプリ直下に置くファイル(そのまま)
├── apps.py
├── admin.py
├── models/                  # 永続化・状態判定
├── views/                   # HTTPの入出力
├── forms/                   # 入力検証(画面単位。Validation Rules参照)
├── services/                # 業務ロジック・トランザクション境界
├── selectors/               # Viewの読み取り窓口(Selector Rules参照)
├── validators/              # Pure Functionの検証ロジック(Validator Rules参照)
├── errors/                  # DomainError(言語非依存。Error Rules参照)
├── messages/                # DomainErrorの日本語文言(Message Rules参照)
├── rules/                   # Form/Validator/Serviceが共有する形式的制約(Rules Directory Rules参照)
├── lib/                     # 上記のどれにも属さない、app内で共有するコード
│   ├── __init__.py
│   ├── auth.py              # 認証ロジック(ログイン等、誰であるかの検証)
│   └── utils.py             # 汎用ユーティリティ
└── templates/
    └── common/              # appアプリ内で共有するパーシャルテンプレート
        ├── _navbar.html
        └── _messages.html
common/                    # 複数アプリ間で共有するモジュール(実際に複数アプリができてから使う)
├── __init__.py
├── utils.py
└── mixins.py
```

## Form Rules

Djangoの`forms.ModelForm`は使用しない。フォームは常に`forms.Form`を継承し、フィールドを明示的に宣言する。

- **理由**: `ModelForm`は「画面の入力」と「モデルの永続化フィールド」を暗黙に同一視し、`form.save()`でモデルへの書き込みがService層を経由せず直接発生してしまう(Service Rules参照)。フィールドをForm側で明示することで、画面の入力契約がFormだけを見て完結して読み取れるようにする
- **編集画面の初期値**: `ModelForm(instance=...)`のような暗黙のバインドは使わない。`TaskForm(initial=_task_initial(task))`のように、instanceの現在値からinitial dictを明示的に組み立てるヘルパーをView側に用意する(View Method-Branch Rules参照)
- **保存はFormの責務ではない**: `form.save()`はModelForm前提の機能のため存在しない。Formの役割は画面単位の検証(`cleaned_data`を作ること)までで、実際の保存は`app/services/`が`form.cleaned_data`から明示的にモデルへ反映する(Service Rules参照)

### Example

```python
# app/forms/task.py
from django import forms
from app.models import Task


class TaskForm(forms.Form):
    title = forms.CharField(max_length=200)
    description = forms.CharField(widget=forms.Textarea, required=False)
    status = forms.ChoiceField(choices=Task.Status.choices)
```

## Validator Rules

複数のFormフィールド・複数モデルで使い回したい検証ロジックは、Formやモデルファイルに直接書かず`app/validators/`に置く。ValidatorはPure Functionとする。

- **配置**: 関心事ごとに`app/validators/<concern>.py`(複数モデルで共有する形式チェック等)、または単一モデルに強く紐づく場合は`app/validators/<model>.py`に置く
- **Pure Functionの契約**: ORM/DBを呼ばない。Service/Selectorを呼ばない。`request`/`Form`インスタンスに依存しない。値を1つ受け取り、成功時はその値をそのまま返し、失敗時は`app/errors/`の`DomainError`(typed exception)を送出する
- **Djangoの`ValidationError`を使わない**: 失敗時に送出するのはDjangoの`ValidationError`ではなく`DomainError`(Error Rules参照)。Validatorが例外を発生させた時点でエラーの種類(code)が確定している
- **DB状態が必要な検証は対象外**: 重複チェックのようにDBを読む必要がある検証はPure Validatorではない。Formの画面内では完結できないため、Validation Rulesの第2段階(Service)の事前条件チェックとして書く(Validation Rules参照)
- **呼び出し元**: Formの`clean_<field>()`(`DomainError`を`forms.ValidationError`に変換して画面表示する。Message Rules参照)と、Serviceの事前条件チェックの両方から同じ関数を呼べる。呼び出し元ごとにロジックを重複させないための共有点がこのレイヤー

### Example

```python
# app/validators/employee.py
import re
from app import errors
from app.rules.employee import EMPLOYEE_NUMBER_REGEX


# 社員番号の形式を検証する。正しければそのまま返す
def validate_employee_number_format(value: str) -> str:
    if not re.match(EMPLOYEE_NUMBER_REGEX, value):
        raise errors.employee.InvalidEmployeeNumberFormatError()
    return value
```

```python
# app/validators/__init__.py
from . import employee

__all__ = ['employee']
```

## Rules Directory (共有制約) Rules

Validator(Pure Function)とServiceのユースケース検証(Validation Rules/Error Rules参照)の両方から参照したい、DBに依存しない形式的な制約(正規表現・桁数などの定数)は`app/rules/`にまとめる。同じ正規表現が複数箇所に二重に書かれることを防ぐ。

- **配置**: 単一モデルにのみ関係する制約は`app/rules/<model>.py`、複数モデルで共有する制約は関心事ごとのファイル(`app/rules/format.py`等)に置く
- **`app/validators/`(Validator Rules)との違い**: `app/rules/`は正規表現・定数などのDjango非依存の値だけを持つ。`app/validators/`はその定数を使って実際に判定し、失敗時に`DomainError`を送出するPure Functionを置く場所
- **DBを参照しない**: 純粋な定数・正規表現に限る。DBを参照する検証はValidation Rulesに従う

### Example

```python
# app/rules/employee.py

# 社員番号の形式(例: E0001)
EMPLOYEE_NUMBER_REGEX = r'^E\d{4}$'
```

```python
# app/forms/employee.py
from django import forms
from app import errors, messages as app_messages
from app.validators.employee import validate_employee_number_format


class EmployeeForm(forms.Form):
    employee_number = forms.CharField(max_length=10)
    ...

    # 画面単位の形式チェック(Validation Rulesの第1段階)。ValidatorのDomainErrorを画面表示用に変換する
    def clean_employee_number(self):
        value = self.cleaned_data['employee_number']
        try:
            return validate_employee_number_format(value)
        except errors.base.DomainError as error:
            raise forms.ValidationError(app_messages.employee.message_for_error(error)) from error
```

## Mixin/Base Naming Rules

多重継承に使うクラスは、役割によって名前の末尾を使い分ける。

- **`XxxBase`**: そのクラスが「is-a」の主軸(本体)であることを示す。抽象基底クラスとして、そこから具体的なクラスが1本の系譜として派生していくイメージ。
- **`XxxMixin`**: 単体では完結しない、部品としての機能追加であることを示す。他のクラスと組み合わせて使う前提で、単体でインスタンス化されることは想定しない。

### Example

```python
# 「is-a」の主軸となる抽象モデル
class TaskBase(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)


# 部品として機能を追加するだけのmixin
class TimestampMixin:
    updated_at = models.DateTimeField(auto_now=True)


class Task(TaskBase, TimestampMixin):
    ...
```

## Model Table Naming Rules

Djangoのデフォルトのテーブル名(`<applabel>_<モデル名を小文字化しただけの文字列>`)は、複数単語のモデル名だと単語の区切りが分からず読みにくい(例: `ManagementGroup` → `app_managementgroup`)。全モデルで`Meta.db_table`を明示し、アプリ名プレフィックスを付けず、単語間を`_`で区切ったスネークケースのテーブル名にする。

- 単語区切りだけでなくアプリ名プレフィックス(`app_`等)も付けない。テーブル名だけを見て何のデータか分かることを優先する
- モデルを追加・リネームしたら、`Meta.db_table`の設定と対応するマイグレーション(`makemigrations`で生成される`AlterModelTable`)の作成を忘れない

### Example

```python
class ManagementGroup(models.Model):
    class Meta:
        db_table = 'management_group'

    ...
```

## Migration Rules

マイグレーションファイルは、まだどこにも適用されていない間(自分のローカルDB以外に、共有DB・他の開発者・CI等で`migrate`が実行されていない間)は、自由に編集・統合してよい。逆に、一度でも共有された環境に適用されたマイグレーションは書き換えない(適用先の`django_migrations`テーブルとの整合性が壊れるため)。

- 同一ブランチ内(mainに未マージ)で同じモデルへの変更を続ける場合、新しいマイグレーションファイルを都度追加せず、まだ未適用のマイグレーションファイルを直接編集して1つにまとめる。
- ブランチがmainにマージされた後にさらに変更が必要になった場合は、既存のマイグレーションを書き換えず、新しいマイグレーションファイルを追加する。
- マイグレーションを直接編集した後は、`python manage.py makemigrations --check --dry-run`でモデル定義とのズレがないことを確認する。

## Seed Data Rules

開発・動作確認用のシードデータ生成ロジックは、models/views/forms等と同様にモデルごとにファイル分割し、`app/seeds/` ディレクトリに置く。`app/management/commands/seed_database.py` は各`app/seeds/*.py`の`create()`を呼び出すだけの薄い実装にする。

- **モデルを追加したら、そのモデルにシードデータが必要か検討する**: 画面確認やログインに使うようなモデル(例: Employee)は追加時にシードデータも作成する。参照専用のマスタ的なモデルなど不要な場合はスキップしてよい。
- **配置場所**: `app/seeds/<model>.py` に `create()` 関数を定義する。他のシードから参照される可能性がある場合は、作成したオブジェクトを返す。
- **呼び出し順序**: `seed_database.py`の`handle()`で、モデルの依存関係(外部キー等)を考慮した順序で各`create()`を呼び出す。
- **シードデータは最小限にする**: ログイン確認用など個別に参照したいレコードは社員番号などを固定して少数だけ作る。一覧・ページネーションなど「複数件あること」の確認が必要な場合のみ、`Faker`(`Faker('ja_JP')`)でダミーデータを追加生成する。用途がないのに機械的に大量のダミーデータを生成しない。
- **パスワードは固定の簡易値でよい**: `password123` のような開発用の固定パスワードを使う(本番相当のランダム生成は不要)。

### Example

```
app/seeds/
├── __init__.py       # from . import employee のようにモジュール単位でインポート
└── employee.py        # def create(): ...
```

```python
# app/seeds/employee.py
from django.contrib.auth.models import User
from faker import Faker
from app.models import Employee

fake = Faker('ja_JP')
DUMMY_EMPLOYEE_COUNT = 10


# 社員のシードデータを作成する
def create():
    # ログイン確認用に社員番号を固定した社員
    _create_employee('E0001', '太郎', '山田', is_staff=True)
    _create_employee('E0002', '花子', '鈴木')

    # 一覧・ページネーション確認用のダミー社員
    for i in range(1, DUMMY_EMPLOYEE_COUNT + 1):
        _create_employee(f'E9{i:03d}', fake.first_name(), fake.last_name())


def _create_employee(employee_number, first_name, last_name, is_staff=False):
    user = User.objects.create_user(
        username=employee_number, password='password123',
        first_name=first_name, last_name=last_name, is_staff=is_staff,
    )
    return Employee.objects.create(user=user, employee_number=employee_number)
```

```python
# app/management/commands/seed_database.py
from django.core.management.base import BaseCommand
from app import seeds


class Command(BaseCommand):
    help = '動作確認用のシードデータを投入する'

    def handle(self, *_args, **_options):
        seeds.employee.create()
```

## Validation Rules

検証は1箇所に集約せず、判断できるタイミングごとに3段階へ分ける。同じチェックをどの段階にも重複して書かない。

1. **Form(画面単位)**: 今の画面の入力形式・必須項目など、その画面だけで判断できる検証。`clean_<field>()`/`clean()`に書く(Form Rules参照)。再利用したい判定は`app/validators/`のPure Functionを呼ぶ(Validator Rules参照)。他画面の未入力や、DBを参照する業務判断(重複チェック等)はここに書かない
2. **ユースケース検証(Service)**: 確定・状態遷移など、複数の入力が揃って初めて判断できる業務ルール。DB参照を伴う重複チェックなどの事前条件もここに書く。`app/services/`が`app/errors/`の`DomainError`を直接送出する(Djangoの`ValidationError`を介さない。Error Rules/Service Rules参照)
3. **DB制約(最終防衛)**: `unique=True`/`Meta.constraints`(`UniqueConstraint`/`CheckConstraint`)など、DB自身が保証できる不変条件だけを書く。Modelに独自の`clean()`/`full_clean()`は実装しない(禁止。下記「Model(第3段階): 禁止事項」参照)

「その画面の入力だけで判断できるか(1)」「業務全体の整合性が必要か(2)」「DBが機械的に保証できる制約か(3)」で置き場所を切り分ける。予測可能な業務エラー(利用者が普通に発生させ得るもの)はDjangoの`ValidationError`を経由させず、2の段階でServiceが`DomainError`を直接送出する形にする。複数モデルを跨ぐ整合性(例: 親部門と部門が同じ会社に属すること)のようにDB制約として表現できない業務ルールは、2のService事前条件チェックが唯一の砦になる。実装漏れがないことはレビューで担保する。

### Model(第3段階): 禁止事項

- **`clean()`/`full_clean()`の独自実装・呼び出しを禁止する**: Modelはフィールド定義・DB制約・自身のインスタンス値だけで完結するpureなメソッド(状態判定など)だけを持つ。DBを参照する検証やモデル間の整合性チェックはModelに書かない
- **`save()`/`delete()`のオーバーライドを禁止する**: Serviceが呼び出しの起点を一元管理する(Service Rules参照)。Modelの`save()`にフックを増やさない
- **Modelのメソッド内でORMクエリを呼ばない**: `self.related_set.filter(...)`のような関連経由の暗黙アクセスも含め、Model メソッドは自分自身の属性値だけで判定する。DBを参照する判定はSelector(読み取り)かService(書き込み前提条件)に置く
- **重複チェック等、DBで機械的に保証できる制約は`Meta.constraints`に書く**: `models.UniqueConstraint(fields=[...])`のようにDB自身が守れる形に落とし込めるなら、Serviceの事前条件チェックに加えてDB制約も設定する(競合時の最終防衛)。DB制約で表現できない場合はServiceの事前条件チェックのみになる

### Example

```python
from django.db import models


class DepartmentQuerySet(models.QuerySet):

    # 同じ会社・同じ名前の部門に絞り込む(自分自身は除く)。Serviceの事前条件チェックから呼ぶ(QuerySet Rules参照)
    def duplicate_of(self, *, company, name, exclude_pk=None):
        queryset = self.filter(company=company, name=name)
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset


class Department(models.Model):
    objects = DepartmentQuerySet.as_manager()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        # DB自身が保証できる制約(競合時の最終防衛)
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='unique_department_name_per_company'),
        ]
```

```python
class DepartmentHierarchy(models.Model):
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    parent_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.CASCADE)
    # 「parent_departmentはdepartmentと同じ会社に属する」はモデルを跨ぐ整合性でありDB制約で表現できないため、
    # Serviceの事前条件チェック(下記set_parent_department())が唯一の検証になる
```

```python
# app/services/department.py
from app import errors


def rename(*, department: Department, name: str) -> Department:
    # 1. 検証(事前条件。DjangoのValidationErrorを介さずDomainErrorを直接送出する)
    if Department.objects.duplicate_of(company=department.company, name=name, exclude_pk=department.pk).exists():
        raise errors.department.DuplicateDepartmentNameError()

    # 2. 変更(UniqueConstraintが競合時の最終防衛になる。IntegrityErrorはバグとしてそのまま伝播させる)
    department.name = name
    department.save(update_fields=['name'])
    return department


# 親部門を設定する(複数モデルを跨ぐ整合性はDB制約で表現できないため、ここが唯一の検証になる)
def set_parent_department(*, hierarchy: DepartmentHierarchy, parent_department: Department) -> DepartmentHierarchy:
    if parent_department.company_id != hierarchy.department.company_id:
        raise errors.department.ParentDepartmentCompanyMismatchError()

    hierarchy.parent_department = parent_department
    hierarchy.save(update_fields=['parent_department'])
    return hierarchy
```

## Error Rules

予測可能な業務失敗(利用者が普通に発生させ得るもの)は、Djangoの`ValidationError`を経由させず、`app/errors/`に定義する言語非依存の`DomainError`(typed exception)として最初から直接送出する。エラーの発生条件(コード)と表示文言(日本語)を分離し、文言変更・多言語化のためにドメイン層を触らずに済むようにする。

- **配置**: 基底クラスを`app/errors/base.py`に置き、モデル・業務領域ごとに`app/errors/<model>.py`へ具体的なエラーを定義する。`__init__.py`はView/Serviceと同様にモジュール単位でインポートする
- **形**: `code`(文字列)と`params`(dict)を持つdataclassベースの例外にする。メッセージ文字列は持たない
- **業務エラーにDjangoの`ValidationError`を使わない**: `DomainError`はDjangoの`ValidationError`を継承・変換せず、独立した例外として定義する。ModelもValidatorも`clean()`/`full_clean()`を使わないため(Validation Rules/Validator Rules参照)、業務エラーの経路にDjangoの`ValidationError`は登場しない。Formの`clean_<field>()`が画面表示のために送出する`forms.ValidationError`は、あくまで画面(Django Form)自身の仕組みであり、`DomainError`とは別物として扱う
- **`app/models/`との関係**: 状態判定(`can_complete()`等)はこれまで通りModelが真偽値メソッドとして持ち、`DomainError`の送出はService側が担う(Service Rulesの「modelとの役割分担」参照)。Model自身は`app/errors/`をimportせず、`DomainError`を送出しない
- **programmer errorを握り潰さない**: DB制約違反(`IntegrityError`)など、Serviceの事前条件チェックをすり抜けて発生した想定外のエラーを`DomainError`に変換して隠さない。バグまたは競合として通常の例外のまま伝播させる
- `app/errors/`は他のどの層(`views/`, `messages/`等)にも依存しない
- **importの書き方**: 共通基底クラスの`DomainError`は名前衝突の心配がないため`from app.errors.base import DomainError`のように直接importしてよい。モデル固有のエラークラス(`TaskNotCompletableError`等)は他層と同様に`from app import errors`のうえで`errors.<model>.XxxError`とモジュール修飾して参照する(View/Service/Selectorと同じ規約)

### Example

```python
# app/errors/base.py
from dataclasses import dataclass, field
from typing import Any


@dataclass(eq=False)
class DomainError(Exception):
    code: str
    params: dict[str, Any] = field(default_factory=dict)
```

```python
# app/errors/task.py
from app.errors.base import DomainError


# 未完了の子タスクが残っているため完了できない
class TaskNotCompletableError(DomainError):
    def __init__(self, *, task_id: int) -> None:
        super().__init__(code='task_not_completable', params={'task_id': task_id})
```

```python
# app/errors/department.py
from app.errors.base import DomainError


# 同じ会社内に同名の部門が既に存在する(Service側の事前条件チェックで送出)
class DuplicateDepartmentNameError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='duplicate_department_name')


# 親部門が同じ会社に属していない(Service側の事前条件チェックで送出)
class ParentDepartmentCompanyMismatchError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='parent_department_company_mismatch')
```

```python
# app/errors/employee.py
from app.errors.base import DomainError


# 社員番号の形式が不正(Validatorから送出)
class InvalidEmployeeNumberFormatError(DomainError):
    def __init__(self) -> None:
        super().__init__(code='invalid_employee_number_format')
```

```python
# app/errors/__init__.py
from . import base
from . import department
from . import employee
from . import task

__all__ = ['base', 'department', 'employee', 'task']
```

## Message Rules

Error Rulesで定義した`DomainError`のコードを日本語文言に変換する処理は、モデル・業務領域ごとに`app/messages/<model>.py`にまとめる。ドメイン層(`models/`, `services/`, `errors/`)は日本語文言を一切持たない。

- **配置**: `app/messages/<model>.py`に、そのモデルに関する`DomainError`のコード→文言の対応表(`ERROR_MESSAGES`)と、対応する`message_for_error()`関数を定義する
- **Djangoの`django.contrib.messages`との名前衝突**: Viewでは`from django.contrib import messages`を使うため、`app/messages/`パッケージは`from app import messages as app_messages`のようにエイリアスしてimportし、どちらを指しているか一目で分かるようにする
- **Viewでの使い方**: Serviceが送出した`DomainError`をViewの`try/except`で受け、`message_for_error()`で文言化してから`django.contrib.messages.error()`に渡す
- **Formでの使い方**: `app/validators/`のPure Functionが送出した`DomainError`をFormの`clean_<field>()`が受け、`message_for_error()`で文言化してから`forms.ValidationError(text)`として画面表示する(Form Rules/Validator Rules参照)。ここでも文言のハードコードはしない
- **成功時の文言**: 成功メッセージ(`messages.success()`)は業務エラーではないため`DomainError`を経由しない。従来通りView側にそのまま日本語文字列で書いてよい
- **未知のコード**: 対応表にないコードのために、`message_for_error()`はデフォルトの汎用メッセージ(例:「処理を完了できませんでした。」)を返すようにする

### Example

```python
# app/messages/task.py
from app.errors.base import DomainError

ERROR_MESSAGES = {
    'task_not_completable': '未完了の子タスクが残っているため、このタスクは完了できません。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
```

```python
# app/messages/employee.py
from app.errors.base import DomainError

ERROR_MESSAGES = {
    'invalid_employee_number_format': '社員番号は E0001 のような形式で入力してください。',
}


def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '入力内容を確認してください。')
```

```python
# app/messages/__init__.py
from . import employee
from . import task

__all__ = ['employee', 'task']
```

## Service Rules

モデルへの書き込みは、すべて`app/services/`を経由する。viewから`form.save()`/`Model.objects.create()`/`instance.save()`/`instance.delete()`を直接呼ばない。

処理の複雑さによって置き場所を変えない。単純な作成・更新であっても例外を設けない。複雑さで分岐させると「これはserviceに置くべきか」という判断が毎回発生し、実装者ごと・セッションごとにブレるため。単純な処理のserviceは数行になるが、後から業務ルールが増えたときにviewを触らずに済み、変更のdiffが「機能追加」だけになる。

読み取りは対象外。Viewからの読み取りはすべてSelector Rulesに従い`app/selectors/`に置く。serviceは書き込み専用とする。

**serviceはselectorを呼ばない。** 事前条件チェックのためにDBを読む必要がある場合(重複チェック等)も、Selectorは経由せずservice自身がORM/QuerySetで直接読む(QuerySet Rulesのカスタムメソッドは共有してよい)。読み取りロジックの再利用より依存方向を優先する。同じ理由でSelectorもserviceを呼ばない(Selector Rules参照)。

### 構成

- `app/services/<model>.py`に関数として定義する。`__init__.py`では`views/`と同様にモジュール単位でインポートし、呼び出し側は`services.<model>.<関数名>`の形で参照する
- 1関数1ユースケースとする。`TaskService`のようなクラスに操作を集約しない。クラスに集約するとモデル単位で肥大化し、分割できなくなる
- 関数名は業務操作名にする(`complete`, `approve`, `cancel`)。単純なCRUDは`create`/`update`/`delete`でよい
- ファイルが肥大化したら、関数の集合であることを活かして`app/services/<model>/`ディレクトリに分割する。`__init__.py`で再エクスポートすれば呼び出し側は変更不要

### 関数の書き方

- 引数はキーワード専用(`*`以降)にする。呼び出し側で各引数の意味が読めるようにするため
- `HttpRequest`を受け取らない。管理コマンド・バッチ・テストから同じ関数を呼べるようにするため。検証済みのフォーム(`Form`インスタンス)は受け取ってよい
- 引数・戻り値の型注釈、使わない引数を持たないことについてはFunction Signature Rulesに従う
- `@transaction.atomic`はserviceに付ける。viewとmodelには書かない。1つの業務操作 = 1つのトランザクションとする
- serviceは他のserviceパッケージを呼ばない。`services/task.py`から`services/project.py`を呼ばない。トランザクション境界が追跡できなくなるため。同一ファイル内のprivateヘルパー(`_`始まり)への切り出しは可

### 関数内部の並び順

処理は以下の順に書く。この順序により、ガード節が先頭に集まり、外部への通知がDB変更の確定後になる。該当しない段階は省略してよい。

1. **検証** — 業務条件を満たさなければ`app/errors/`の`DomainError`を送出して終了(Error Rules参照)
2. **変更** — モデルの更新・関連レコードの作成
3. **記録** — 履歴・監査ログ
4. **通知** — メール送信・外部システム連携

通知は`transaction.on_commit()`に包む。トランザクション内で直接実行すると、後続処理がロールバックしても通知だけが送信される。

### serviceが持たないもの

- `django.contrib.messages`の呼び出し
- 日本語のエラー文言(`DomainError`のcodeのみ送出し、文言は`app/messages/`が担当。Message Rules参照)
- `redirect`/HTTPステータス/テンプレート名
- `get_object_or_404`(Selector Rules参照)
- 画面遷移に関する判断

業務条件を満たさない場合は、リダイレクトではなく`DomainError`を送出する(Error Rules参照)。viewが受け取って`app/messages/`で文言化し(Message Rules参照)、`messages`と画面遷移に変換する。

### modelとの役割分担

serviceが持つのは操作の手順であり、状態の意味ではない。

- 「このオブジェクトが今どういう状態か」の判定はmodelに置く(`task.can_complete()`, `task.is_overdue()`)。テンプレートから`{% if task.can_complete %}`と呼べるのもmodel側にある場合のみ
- 「その状態でこの操作をしてよいか」の判断と、実際の手順はserviceに置く

判定ロジックをserviceに書くとserviceだけが太り、modelが空になる。判定はmodelへ、手順はserviceへ寄せる。

### Example

```python
# app/models/task.py

# タスク管理のためのモデル
class Task(models.Model):
    ...

    # 完了可能な状態かどうか(自身のstatusのみで判定するpureなメソッド)
    def can_complete(self):
        return self.status != Task.Status.COMPLETED
```

```python
# app/services/task.py
from django.db import transaction
from app import errors

# タスクを作成する(ModelFormを使わないため、cleaned_dataから明示的にモデルへ反映する)
def create(*, form: TaskForm) -> Task:
    return Task.objects.create(
        title=form.cleaned_data['title'],
        description=form.cleaned_data['description'],
        status=form.cleaned_data['status'],
    )

# タスクを完了にする
@transaction.atomic
def complete(*, task: Task, operator: User) -> Task:
    # 1. 検証(自身のstatusはModelのpureなメソッドで判定し、DBを参照する子タスクの状態はここで直接読む)
    if not task.can_complete():
        raise errors.task.TaskNotCompletableError(task_id=task.id)
    if task.children.exclude(status=Task.Status.COMPLETED).exists():
        raise errors.task.TaskNotCompletableError(task_id=task.id)

    # 2. 変更
    task.status = Task.Status.COMPLETED
    task.completed_at = timezone.now()
    task.save(update_fields=['status', 'completed_at'])

    # 3. 記録
    TaskHistory.objects.create(task=task, action='completed', operator=operator)

    # 4. 通知
    transaction.on_commit(lambda: send_completion_notice(task))
    return task
```

```python
# app/views/task.py
from app import messages as app_messages
from app.errors.base import DomainError

# タスク完了処理を行う
def _complete_task(request, task):
    try:
        services.task.complete(task=task, operator=request.user)
    except DomainError as error:
        messages.error(request, app_messages.task.message_for_error(error))
        return redirect('app:task_show', pk=task.pk)

    messages.success(request, 'タスクを完了しました。')
    return redirect('app:task_show', pk=task.pk)
```

```python
# app/services/__init__.py
from . import task

__all__ = ['task']
```

## Selector Rules

**Viewの読み取りはすべてSelectorを経由する。** ViewはModel/QuerySetを直接呼ばない(`get_object_or_404`も含む)。単一取得・一覧取得の両方を`app/selectors/<model>.py`に関数として置く。

- **配置**: `app/selectors/<model>.py`に関数として定義する。`__init__.py`はView/Serviceと同様にモジュール単位でインポートし、呼び出し側は`selectors.<model>.<関数名>`の形で参照する
- **命名**: 単一取得は`get_<noun>`、一覧取得は`list_<複数形>`とする(例: `get_task`, `list_tasks`)
- **単一取得**: keyword-only引数を受け取り、`get_object_or_404`で取得する。404にするのは「存在しない/権限のスコープ外」だけ。所有者・権限によるスコープはQuerySet Rulesのカスタムメソッド(`owned_by`等)に寄せ、selectorはそれを`get_object_or_404`に渡すだけにする
- **業務ルールによる操作不可(ステータスが不正・ロック中など)は404にしない**: 「存在はするが今は編集できない」はSelectorではなくServiceが`DomainError`を送出する形にする(Error Rules参照)。混同するとURLを直接叩いた場合の挙動(404 かエラーメッセージか)が食い違う
- **一覧取得**: ページネーション等の都合があるため、評価前の`QuerySet`を返す。Viewがそれをページネーションする
- **selectorはserviceを呼ばない。書き込みも行わない**: 読み取り専用に徹する(QuerySet Rulesと同じ制約)
- 権限スコープが異なる複数の取得経路がある場合(編集用/参照用等)は、`get_task_for_edit`のように用途で関数を分ける

### Example

```python
# app/selectors/task.py
from django.contrib.auth.models import AbstractBaseUser
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from app.models import Task


# 編集対象のタスクを取得する(担当者以外には404)
def get_task_for_edit(*, task_id: int, user: AbstractBaseUser) -> Task:
    return get_object_or_404(Task.objects.assigned_to(user), pk=task_id)


# タスク一覧を取得する(未評価のQuerySetを返す。ページネーションはView側)
def list_tasks() -> QuerySet[Task]:
    return Task.objects.with_details()
```

```python
# app/selectors/__init__.py
from . import task

__all__ = ['task']
```

```python
# app/views/task.py
from app import selectors

@login_required
def index(request: HttpRequest) -> HttpResponse:
    tasks_qs = selectors.task.list_tasks()
    paginator = Paginator(tasks_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/task/index.html', {'tasks': page_obj, 'page_obj': page_obj})


@login_required
def edit(request: HttpRequest, pk: int) -> HttpResponse:
    task = selectors.task.get_task_for_edit(task_id=pk, user=request.user)
    ...
```

## QuerySet Rules

繰り返し使う絞り込み条件は、viewやserviceに書かず、カスタムQuerySetのメソッドとして定義する。同じ`filter()`が複数箇所に散ることを防ぎ、条件に業務上の名前を与えるため。

- `app/models/<model>.py`内に、対応するモデルと同じファイルで定義する。全モデル分を1ファイルに集約しない
- モデルには`objects = XxxQuerySet.as_manager()`で紐づける
- QuerySetは読み取り専用とする。状態変更や副作用を持たせない
- 一覧表示で関連を辿る場合の`select_related`/`prefetch_related`もQuerySetメソッドにまとめる

### Example

```python
# app/models/task.py

class TaskQuerySet(models.QuerySet):

    # 未完了のタスクに絞り込む
    def incomplete(self):
        return self.exclude(status=Task.Status.COMPLETED)

    # 期限を過ぎた未完了タスクに絞り込む
    def overdue(self):
        return self.incomplete().filter(due_on__lt=timezone.localdate())

    # 一覧表示で必要な関連をまとめて読み込む
    def with_details(self):
        return self.select_related('assignee').prefetch_related('children')


class Task(models.Model):
    objects = TaskQuerySet.as_manager()
    ...
```
