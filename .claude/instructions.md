# Django Development Guidelines

> **このファイルの位置づけ**: 別のDjangoプロジェクトにそのままコピーして使う、再利用可能な開発規約集(`CLAUDE.md`が「雛形として引き継ぐ」と定義している章の一つ)。書く内容は「このプロジェクトの現在の状態」ではなく、Djangoプロジェクト一般に適用できる規約・パターンにすること。
>
> - 各ルールの例に出てくる`Task`/`Employee`等のモデル名は、あくまでパターンを説明するための例示。実際のこのプロジェクトのモデル・ファイル構成と完全に一致している必要はない(コピー先の別プロジェクトではどのみち別のモデル名になる)
> - 一方、規約・パターンの説明自体に矛盾や誤りがある場合は、コピー先でも同じ混乱を招くため修正する

## File Structure Rules

models、forms、views、validators、tests、templatesはディレクトリ化し、機能ごとにファイル分割してください。検証ロジックがForm/Validator/View/DB制約のどこに属するかはValidation Rulesを参照。

Djangoが標準で持たないレイヤー(`services/`、`selectors/`のような独自ディレクトリ)は既定では作らない。読み書きの置き場所はDjango本来の位置、すなわちmodel・form・viewに寄せる(View Write Rules/QuerySet Rules参照)。

### Examples
- models/todo.py
- views/todo.py
- forms/todo.py
- validators/todo.py
- errors/todo.py
- tests/unit/models/todo_test.py
- tests/unit/forms/todo_test.py
- tests/unit/views/todo_test.py
- tests/unit/validators/todo_test.py
- tests/e2e/todo_test.py

各ディレクトリに__init__.pyを配置すること。

`tests/unit/`配下は、ソース側の`models/`, `forms/`, `views/`, `validators/`, `lib/`と対応するレイヤーごとのディレクトリにさらに分割する(Railsの`test/models/`, `test/controllers/`に相当)。`app/lib/`(`auth.py`/`permissions.py`等、app内で共有するロジック。詳細はCommon Module Rulesを参照)のテストも同様に`tests/unit/lib/`に置く(例: `tests/unit/lib/auth_test.py`)。`app/rules/`(役割はRules Directory Rulesを参照)は単純な定義の並びであることが多く、分岐ロジックが生じた場合のみテストディレクトリを追加する。`tests/e2e/`はページ単位のテストのため、このレイヤー分割は行わない。

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
    task = get_object_or_404(Task.objects.assigned_to(request.user), pk=pk)  # 読み取りはRead Rules参照
    if request.method == 'POST':
        return _update_task(request, task)
    return _display_edit_form(request, task)


# (他の公開アクションが続く)


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# 編集フォームを表示する
def _display_edit_form(request, task):
    form = TaskForm(instance=task)
    return _render_edit_form(request, task, form)


# タスクの更新処理を行う
def _update_task(request, task):
    form = TaskForm(request.POST, instance=task)  # instanceを渡し忘れると新規作成になる(Form Rules参照)
    if not form.is_valid():
        return _render_edit_form(request, task, form)
    form.save()
    messages.success(request, 'タスクを更新しました。')
    return redirect('app:task_show', pk=task.pk)


# タスク編集フォームのレンダリング
def _render_edit_form(request, task, form):
    return render(request, 'app/task/edit.html', {'form': form, 'task': task})
```

リクエストを扱うprivateヘルパーは、フォームの束縛・権限判定・messages・リダイレクトを行う。モデルへの書き込みと業務ルールの検証は、同じファイル内の書き込みヘルパーに置く(View Write Rules参照)。

更新系のPOSTは、成功時に必ずリダイレクトする(POST-Redirect-GET)。ブラウザの再送信を防ぎ、「GETは表示・POSTは更新」の境界を保つため。

## Control Flow Rules

`if`のネストを深くしない。条件が成立しない場合や異常系は早期に`return`し、`else`で包まずインデントを1段に保つ(ガード節/早期return)。ビューに限らず、モデル・フォーム・共有モジュールなど全てのPythonコードに適用する。

### Example

```python
# 避ける書き方(ネストが深い)
def _create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = Task.objects.create(**form.cleaned_data)
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
    task = Task.objects.create(**form.cleaned_data)
    messages.success(request, 'タスクを作成しました。')
    return redirect('app:task_show', pk=task.pk)
```

## Function Signature Rules

関数・メソッドのシグネチャは、実際の利用実態を正確に表すものにする。ビューに限らず、モデル・フォーム・共有モジュールなど全てのPythonコードに適用する。

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

## ADR Rules

設計上の決定のうち、**実在した代替案を却下して選んだもの**だけを ADR (Architecture Decision Record) として `docs/adr/` に残す。規約そのものはこのファイルに書き、ADRの主眼は「なぜ他の案ではないのか」に置く。決定の内容はこのファイル側に書き、ADRの `## 決定` は2〜3行の要約に留める(同じ説明を両方に展開しない)。

> **このテンプレートには ADR を同梱しない。** `docs/adr/` はコピー先のプロジェクトで作り始める。`ModelForm`を使わない・Modelにライフサイクルメソッドを実装しない等、この規約集が既に定めている決定は、代替案の検討がテンプレート側で完了しており、コピー先で記憶に基づいて後から書けない(下記「AIの関与」の推測禁止に抵触する)。ADRに残すのはコピー先で新たに下した決定に限る。

- **配置**: `docs/adr/NNNN-<kebab-case-title>.md`。番号は4桁の連番で、ファイル名は番号から始める(`adr-`のようなプレフィックスを付けない)。検討が流れて欠番になっても埋めない
- **ヘッダ**: 本文冒頭に `Status` と `Date`(`YYYY-MM-DD`、決定した日。supersedeされても変えない)を置く。supersede 関係がある場合は新しい側に `Supersedes: ADR-NNNN` を足す
- **`Status` の値**: `Accepted` か `Superseded by ADR-NNNN` のみ。「決定した直後に書く」運用のため `Proposed` は使わない
- **本文の構成**: `## 背景` → `## 決定`(上記のとおり要約のみ) → `## 却下した案`(1案ごとに「案 → 却下理由」を書く) → `## 影響`(移行作業と、影響を受けるファイルの列挙)
- **索引**: `docs/adr/README.md` に「番号・タイトル・Status」の表を置く。ADRを追加・変更したら索引も同じPRで更新する。`docs/adr/` 内で既存の記述を書き換えてよいのは、索引と、supersedeされた側のADRの `Status` 行だけ(ADR本文は書き換えない。下記「追記のみ」)
- **書くタイミング**: 決定した直後に、規約の更新と同じPRに含める。後から書くと検討の記憶が失われ、結論だけの文書になる。結論はこのファイルに書いてあるため、それではADRの価値が無い

### 書く対象

「却下した案」に書くことが無いなら、それはADRにしない判断だったということ。

- **書く**: コピー先で、Djangoの標準的な書き方をあえて採らないと決めたとき。フレームワーク・ライブラリの選定。**このテンプレートの規約を覆す変更**
- **書かない**: 代替案を検討していない決定(テンプレートのファイル名、命名規則、ディレクトリ構成など)。これらはこのファイルに規約として書けば足りる
- **書かない**: このテンプレートから引き継いだ決定そのもの(`ModelForm`不使用、Modelにライフサイクルメソッド不実装など)。代替案の検討はテンプレート側で済んでおり、コピー先でADR化しようとすると「却下した案」を推測で書くことになる

`## 却下した案` が空のADRはマージしない(却下した案が無いならADRにしないという判断)。

テンプレートの規約を覆すADRを書く場合、`## 却下した案` にはテンプレートの元方針を挙げ、却下理由は*覆す側の理由だけ*を書く。元方針を採った理由(テンプレート側の意図)はこのファイルの本文にあるので、そこを指すに留め、推測で補わない。

### 追記のみ

一度マージしたADRの本文は書き換えない。決定が変わった場合は新しいADRを追加し、両方に相互参照を書く。

- 新しい側に `Supersedes: ADR-NNNN` を書く
- 古い側の `Status` を `Superseded by ADR-NNNN` に変更する(索引の行も同じPRで合わせる。ずれた場合はADR本体を正とする)。本文・却下した案はそのまま残す
- 古いADRを削除しない。「なぜ以前その案を採ったのか」と「なぜやめたのか」が両方残っていないと、同じ検討が繰り返される
- そのADRを `経緯:` で参照している規約セクションの行を、新しい番号に書き換える(ADR側は追記のみだが、このファイルは常に現在の正解を指す)

### AIの関与

- **AIは自分の判断でADRを作成しない**: 実装中にこのファイルに答えの無い判断をした場合、ADRを書くのではなく、その判断を報告する。ADRを起こすかどうかは人が決める
- **3点が揃うまで着手しない**: 人から「決定」「検討した代替案」「各案の却下理由」の3点が示されて初めて文章化に入る。欠けている項目をAIが補完しない
- **「却下した案」を推測で書かない**: 実際に検討して捨てた案だけを書く。一般論としてもっともらしい理由を補わない。示されていない案・却下理由があれば、その節を空のまま残して確認する
- **AIが担当するのは機械的な部分**: 示された内容の文章化、採番、相互参照(`Supersedes`/`Superseded by`)の追記、索引の更新、影響範囲のファイル列挙

### リンクの向き

参照は一方向にする。双方向にするとリンクが腐る。

- ADRの対象になった規約セクションの末尾にだけ、`経緯: ADR-NNNN` を一行で書く(この方向のみ)。原則 `##` セクションの末尾に付け、対象が特定の `###` サブセクションに限られる場合だけそちらに付ける。同じADRへの `経緯:` を複数箇所に書かない
- **コードからADRへのリンクは書かない**: 決定が変わるとADR番号が変わり、コード側のコメントが古い番号を指したまま残る。コメント量も元に戻る
- **例外**: 現在の規約に違反しているように見えるコードにだけ、対象外である旨と期限をコメントで書く(移行期間中の箇所など)

### Example

以下は書式の例示。題材(非同期処理基盤の選定)はテンプレートと無関係な、コピー先で新たに下した決定の想定。コピー先が最初 ADR-0003 で django-q2 を採用し、後に Celery へ移行して ADR-0009 で置き換えた、という筋にしている。番号・日付は仮。

```
docs/adr/
├── README.md                          # 索引(番号・タイトル・Status)
├── 0003-async-backend-django-q2.md    # Superseded by ADR-0009
└── 0009-async-backend-celery.md
```

```markdown
# ADR-0009: 非同期処理基盤を Celery + Redis にする

Status: Accepted
Date: 2026-08-20
Supersedes: ADR-0003

## 背景

定期実行ジョブが増え、ワーカーを複数ホストに分散する必要が出てきた。
ADR-0003 で採用した django-q2 のスケジューラは単一プロセス前提で、
水平スケールするとジョブが重複して実行される。

## 決定

非同期処理基盤に Celery + Redis を使う。タスクは `app/tasks/<model>.py` に置き、
書き込みヘルパー(View Write Rules参照)から `transaction.on_commit()` 経由で enqueue する。

## 却下した案

- django-q2 を使い続ける (ADR-0003 の方針)
  → スケジューラが単一プロセス前提で、水平スケール時にジョブが重複する
- RQ (Redis Queue) にする
  → 再試行・レート制限・優先度つきキューを自前で実装することになる
- クラウドのマネージドキュー (SQS 等) にする
  → ローカル開発で別途エミュレータが要り、devcontainer だけで完結しなくなる

## 影響

`config/settings.py` に Celery 設定を追加。`app/tasks/` を新設。
ローカルのコンテナ構成に redis を追加。`django-q2` 依存を削除。
```

```markdown
<!-- docs/adr/README.md -->
| No | タイトル | Status |
|----|---------|--------|
| 0003 | 非同期処理基盤に django-q2 を採用 | Superseded by ADR-0009 |
| 0009 | 非同期処理基盤を Celery + Redis にする | Accepted |
```

コピー先はこの決定に対応する規約をこのファイルに足し、そのセクション末尾に `経緯:` を書く。

```markdown
<!-- コピー先がこのファイルに追加した規約セクション -->
## 非同期処理 Rules

...

経緯: ADR-0009
```

例外箇所のコメントは、規約に違反して見えるコードにのみ書く。規約に従っている箇所には何も書かない。

```python
# 移行期間中のため django-q2 のまま。ADR-0009 の対象外(2026-12 までに app/tasks/ へ移す)
@background
def send_daily_digest():
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

`app/lib/`は、`models/`/`views/`/`forms/`のいずれにも属さない補助的なコードの置き場である。業務ロジック(モデルへの書き込みを伴う処理)は`app/lib/`に置かず、その操作を行うviewに置く(View Write Rules参照)。

- **1つのアプリ内で共有**: `app/lib/` に置く(Railsの`lib/`相当)。`urls.py`/`apps.py`/`admin.py`のような、Djangoの規約でアプリ直下に置くと決まっているファイルはそのままアプリ直下に残し、開発者が追加した「app内で共有するロジック」だけを`app/lib/`にまとめる。役割ごとにファイルを分ける: 認証(ログイン等、誰であるかの検証)は`app/lib/auth.py`、汎用ユーティリティは`app/lib/utils.py`(増えてきたら`app/lib/utils/`ディレクトリ化し、関心事ごとにファイル分割する。例: `utils/date.py`)。ナビゲーションバー・フラッシュメッセージ表示のような特定のモデルに属さないパーシャルテンプレート(`app/templates/common/`)も同じ考え方で、このアプリ専用の置き場に置く。「複数アプリ間で共有」に見えても、実際に共有先の別アプリが存在しない限りは、このアプリ内に留める。バリデーション(Pure Function)や権限判定は補助的な共有コードではなく`app/validators/`・`app/permissions/`という同列の層として最初から扱う(Validator Rules参照)。
  - 例外: `app/management/commands/`(Djangoがこの場所を前提にコマンドを自動検出する)と`app/seeds/`(Seed Data Rules参照、モデルごとのデータ生成スクリプト群という別カテゴリ)は`app/lib/`に含めない。
  - **`app/lib/`配下のモジュールが肥大化した場合の昇格**: 関心事が独立したサブシステムと呼べる規模になった場合、`app/permissions/`のように`models/`/`views/`/`forms/`等と同列のトップレベルディレクトリへ昇格してよい。昇格後は他のトップレベルディレクトリと同じ構成規則(ディレクトリ化・`__init__.py`配置・テストディレクトリの対応)に従う。
- **複数アプリ間で共有**: `app/` と同列に共有専用アプリ `common/` を作り、`INSTALLED_APPS` に登録して置く。これは実際に2つ以上のアプリから使われるようになった時点で行う。

#### 判断に迷った場合

`app/lib/` に置くべきか view に置くべきか迷ったら、次で判断する。

- モデルへの書き込みを行う、またはトランザクションを必要とする → その操作を行うview(View Write Rules参照)
- 値の計算・変換・判定のみで、DBを変更しない → `app/lib/`

```
config/
app/
├── urls.py                  # Djangoの規約でアプリ直下に置くファイル(そのまま)
├── apps.py
├── admin.py
├── models/                  # 永続化・状態判定
├── views/                   # HTTPの入出力・モデルへの書き込み(View Write Rules参照)
├── forms/                   # 入力検証(画面単位。Validation Rules参照)
├── validators/              # Pure Functionの検証ロジック(Validator Rules参照)
├── rules/                   # Form/Validatorが共有する形式的制約(Rules Directory Rules参照)
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

フォームは`forms.ModelForm`を継承し、`Meta`で対象モデルと画面に出すフィールドを宣言する。

- **フィールドはMetaで明示する**: `fields = '__all__'`や`exclude`は使わない。モデルにフィールドを足したときに、画面の入力項目が黙って増えることを防ぐ。画面に出す項目を`fields`に列挙し、その並びが画面の入力契約になる
- **モデル由来の検証はModelFormに任せる**: `max_length`、`unique=True`、`Meta.constraints`の`UniqueConstraint`などは、ModelFormが`full_clean()`を通じて自動で検証する。同じ検証をフォームに重ねて書かない(Validation Rules参照)
- **モデルに無い制約はフォームで明示宣言する**: モデル側がDB制約(`CheckConstraint`)しか持たない範囲指定などは、ModelFormでは導出されない。画面での一次防衛が必要なら、そのフィールドをフォームで明示的に宣言して`min_value`等を与える
- **編集画面の初期値**: `Form(instance=obj)`を使う。initial dictを組み立てるヘルパーは作らない
- **保存**: `form.save()`を使う。モデルのフィールド以外を設定する必要がある場合(作成者の記録など)は`form.save(commit=False)`で受け取り、設定してから`save()`する
- **更新時は必ず`instance=`を渡す**: `Form(request.POST, instance=obj)`とする。渡し忘れると更新ではなく新規作成になり、一意制約のエラーとしてしか気づけない
- **複数モデルにまたがるフォーム**: 主となるモデルのModelFormとし、他モデルの項目はフォームに追加宣言する。追加宣言した項目は`instance`から初期値が入らないため、フォームの`__init__`で補う。保存はviewの書き込みヘルパーが担当する(View Write Rules参照)

### エラー文言

- **モデル由来の検証**: `Meta.error_messages`で上書きする。複合一意制約(`unique_together`相当)は`NON_FIELD_ERRORS`キーを使う
- **複数フィールドにまたがる業務ルール**: `clean()`に書き、`forms.ValidationError`に文言を直接渡す。文言を一元管理したいという理由だけで例外クラスを定義し、`XxxError().message`のように生成して文字列を取り出さない。送出されない例外クラスは実体としては文字列定数であり、型が用途を偽ることになる

### Example

```python
# app/forms/department.py
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS
from app.models import Department


# 部門の新規作成・編集で使うフォーム
class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department
        fields = ['company', 'name']
        widgets = {
            'company': forms.Select(attrs={'class': 'ds-input'}),
            'name': forms.TextInput(attrs={'class': 'ds-input'}),
        }
        error_messages = {
            NON_FIELD_ERRORS: {'unique_together': 'この会社には同じ名前の部門が既に存在します。'},
        }
```

```python
# app/forms/task.py

class TaskForm(forms.ModelForm):
    # モデル側の範囲指定はDB制約(CheckConstraint)のみのため、画面での一次防衛としてここで宣言する
    priority = forms.IntegerField(label='優先度', min_value=1, max_value=5)

    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority']

    # 複数フィールドが揃って初めて判断できる業務ルールはclean()に書く
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('status') == Task.Status.COMPLETED and not cleaned_data.get('description'):
            raise forms.ValidationError('完了にする場合は説明の入力が必要です。')
        return cleaned_data
```

```python
# app/views/task.py

# タスクの新規作成処理を行う
def _create_task(request):
    form = TaskForm(request.POST)
    if not form.is_valid():
        return _render_new_form(request, form)
    task = form.save(commit=False)
    task.created_by = request.user   # モデルのフィールドだが画面の入力項目ではないため、ここで設定する
    task.save()
    messages.success(request, 'タスクを作成しました。')
    return redirect('app:task_show', pk=task.pk)
```

## Validator Rules

複数のFormフィールド・複数モデルで使い回したい検証ロジックは、Formやモデルファイルに直接書かず`app/validators/`に置く。ValidatorはPure Functionとする。

- **配置**: 関心事ごとに`app/validators/<concern>.py`(複数モデルで共有する形式チェック等)、または単一モデルに強く紐づく場合は`app/validators/<model>.py`に置く
- **Pure Functionの契約**: ORM/DBを呼ばない。viewを呼ばない。`request`/`Form`インスタンスに依存しない。値を1つ受け取り、問題がなければ何も返さず、失敗時に`django.core.exceptions.ValidationError`を送出する(Djangoのvalidatorの標準的な形)
- **`code`を必ず付ける**: `ValidationError('文言', code='...')`のように、文言と併せて識別子を渡す。どのルールで落ちたかをテストや構造化ログから判別できるようにするため
- **DB状態が必要な検証は対象外**: 重複チェックのようにDBを読む必要がある検証はPure Validatorではない。モデルの制約として宣言し、ModelFormに検証させる(Validation Rules参照)
- **呼び出し元**: Formの`clean_<field>()`から呼ぶ。`ValidationError`はDjangoがそのフィールドのエラーとして自動で割り当てるため、捕まえて詰め替える必要はない。モデルのフィールドの`validators=[...]`に渡して、そのモデルを扱う全てのフォームに適用することもできる

### Example

```python
# app/validators/employee.py
import re
from django.core.exceptions import ValidationError
from app.rules.employee import EMPLOYEE_NUMBER_REGEX


# 社員番号の形式を検証する
def validate_employee_number_format(value: str) -> None:
    if not re.match(EMPLOYEE_NUMBER_REGEX, value):
        raise ValidationError('社員番号の形式が正しくありません。', code='invalid_employee_number_format')
```

```python
# app/validators/__init__.py
from . import employee

__all__ = ['employee']
```

## Rules Directory (共有制約) Rules

Validator(Pure Function)とviewのユースケース検証(Validation Rules参照)の両方から参照したい、DBに依存しない形式的な制約(正規表現・桁数などの定数)は`app/rules/`にまとめる。同じ正規表現が複数箇所に二重に書かれることを防ぐ。

- **配置**: 単一モデルにのみ関係する制約は`app/rules/<model>.py`、複数モデルで共有する制約は関心事ごとのファイル(`app/rules/format.py`等)に置く
- **`app/validators/`(Validator Rules)との違い**: `app/rules/`は正規表現・定数などのDjango非依存の値だけを持つ。`app/validators/`はその定数を使って実際に判定し、失敗時に`ValidationError`を送出するPure Functionを置く場所
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
from app.models import Employee
from app.validators.employee import validate_employee_number_format


class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['employee_number']

    # 画面単位の形式チェック(Validation Rulesの第1段階)。ValidationErrorはDjangoがこのフィールドに割り当てる
    def clean_employee_number(self):
        value = self.cleaned_data['employee_number']
        validate_employee_number_format(value)
        return value
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

1. **Form(画面単位)**: 画面から入力される値に関する検証はここに集約する。ModelFormを使うため、`max_length`・`unique=True`・`Meta.constraints`の`UniqueConstraint`といったモデル由来の検証は`full_clean()`経由で自動的にこの段階に含まれる。**書く必要があるのは、自動で導出されないものだけ**。すなわち、単一フィールドの形式チェック(`clean_<field>()`)と、複数フィールドが揃って初めて判断できる業務ルール(`clean()`)である。再利用したい判定は`app/validators/`のPure Functionを呼ぶ(Form Rules/Validator Rules参照)
2. **ユースケース検証(View)**: **フォームを伴わない操作**の事前条件。「完了にする」「承認する」のように、画面からの入力ではなく対象の現在状態によって可否が決まるもの。viewの書き込みヘルパーが`django.core.exceptions.ValidationError`を`code`付きで送出し、呼び出し側が受けて`messages.error()`に渡す(View Write Rules参照)
3. **DB制約(最終防衛)**: `unique=True`/`Meta.constraints`(`UniqueConstraint`/`CheckConstraint`)など、DB自身が保証できる不変条件だけを書く。Modelに独自の`clean()`は実装しない(禁止。下記「Model(第3段階): 禁止事項」参照)

「画面の入力に関する判断か(1)」「フォームを介さない操作の可否か(2)」「DBが機械的に保証できる制約か(3)」で置き場所を切り分ける。

**1と3は重複して書かない。** モデルに制約を書けば、ModelFormがそれを画面のエラーに変換する。重複チェックをフォームやviewに手で書き足す必要はない。逆に、DB制約で表現できない業務ルール(例: 権限セット番号がPythonのレジストリに実在すること、親部門と部門が同じ会社に属すること)は1の`clean()`が唯一の砦になる。実装漏れがないことはレビューで担保する。

**エラーの表示位置**: モデル由来の検証はそのフィールドのエラーになり、`clean()`で送出したものはフォーム全体のエラー(non_field_errors)になる。テンプレートは両方を描画できるようにしておく。

### Model(第3段階): 禁止事項

- **`clean()`の独自実装を禁止する**: Modelはフィールド定義・DB制約・自身のインスタンス値だけで完結するpureなメソッド(状態判定など)だけを持つ。DBを参照する検証やモデル間の整合性チェックはModelに書かない。なお`full_clean()`はModelFormが内部で呼ぶ(Form Rules参照)。これはDjangoの標準動作であり、禁止の対象は独自の`clean()`実装である
- **`save()`/`delete()`のオーバーライドを禁止する**: 書き込みの起点はviewが明示的に持つ(View Write Rules参照)。Modelの`save()`にフックを増やさない
- **Modelのメソッド内でORMクエリを呼ばない**: `self.related_set.filter(...)`のような関連経由の暗黙アクセスも含め、Model メソッドは自分自身の属性値だけで判定する。DBを参照する判定はQuerySet(読み取り)かviewの書き込みヘルパー(書き込み前提条件)に置く
- **重複チェック等、DBで機械的に保証できる制約は`Meta.constraints`に書く**: `models.UniqueConstraint(fields=[...])`のようにDB自身が守れる形に落とし込めるなら、ここに書く。ModelFormがこれを画面のエラーに変換するため、同じ検証をフォームやviewに書き足す必要はない。DB制約で表現できない業務ルールのみ、フォームの`clean()`に書く

### Example

```python
from django.db import models


class DepartmentQuerySet(models.QuerySet):

    # 同じ会社・同じ名前の部門に絞り込む(自分自身は除く)。viewの事前条件チェックから呼ぶ(QuerySet Rules参照)
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
    # viewの事前条件チェック(下記_set_parent_department())が唯一の検証になる
```

```python
# app/views/department.py
from django.core.exceptions import ValidationError


# 親部門を設定する(複数モデルを跨ぐ整合性はDB制約で表現できないため、ここが唯一の検証になる)
def _set_parent_department(*, hierarchy: DepartmentHierarchy, parent_department: Department) -> DepartmentHierarchy:
    if parent_department.company_id != hierarchy.department.company_id:
        raise ValidationError(
            '親部門は同じ会社に属している必要があります。', code='parent_department_company_mismatch'
        )

    hierarchy.parent_department = parent_department
    hierarchy.save(update_fields=['parent_department'])
    return hierarchy
```

## View Write Rules

モデルへの書き込みと、それに伴う業務ルールの検証は、その操作を行うviewに置く。`app/services/`のようなDjangoが標準で持たない層を既定では作らない。

そのviewからしか使われない処理を別ディレクトリに置くと、読むときの追跡が増えるだけで、得られるものが無いため。1つのviewと運命を共にする処理は、そのviewと同じファイルにあるのが最も追いやすい。層を跨いで共有したくなった場合の扱いはService Rulesを参照。

### 配置

- 公開アクション(`index`/`show`/`new`/`edit`/`delete`)の下、区切りコメント以降のprivateヘルパー領域に置く(View Method-Branch Rules参照)
- リクエストを扱うヘルパー(`_create_task`等)と、書き込みを行うヘルパーを分ける。前者はフォームの束縛・権限判定・メッセージ・リダイレクトを担当し、後者はDBへの書き込みだけを担当する
- 単一モデルへの単純な作成・更新は、リクエストを扱うヘルパーに直接書いてよい。書き込みヘルパーへの切り出しは、トランザクションが必要なとき(複数モデル・複数レコードにまたがる書き込み)に行う

### 書き込みヘルパーの書き方

- 引数はキーワード専用(`*`以降)にする
- **`HttpRequest`を受け取らない。** 必要な値は呼び出し側が取り出して渡す。将来この処理を管理コマンドやバッチから呼びたくなったとき、HTTPに縛られていない状態を保つため
- 引数・戻り値の型注釈、使わない引数を持たないことについてはFunction Signature Rulesに従う
- `@transaction.atomic`は書き込みヘルパーに付ける。modelには書かない。1つの業務操作 = 1つのトランザクションとする
- **同じファイルに別の意味の同名が同居しないか確認する。** viewは権限判定などを他モジュールからimportしているため、移してきた処理の変数名と衝突することがある(例: ログインユーザー向けの`is_admin()`と、グループの全社管理者フラグ`is_admin`)。衝突する場合は移した側の名前を変え、理由をコメントに残す

### 関数内部の並び順

書き込みヘルパーの処理は以下の順に書く。この順序により、ガード節が先頭に集まり、外部への通知がDB変更の確定後になる。該当しない段階は省略してよい。

1. **検証** — 業務条件を満たさなければ`django.core.exceptions.ValidationError`を`code`付きで送出して終了
2. **変更** — モデルの更新・関連レコードの作成
3. **記録** — 履歴・監査ログ
4. **通知** — メール送信・外部システム連携

通知は`transaction.on_commit()`に包む。トランザクション内で直接実行すると、後続処理がロールバックしても通知だけが送信される。

### 検証の書き方

**画面から入力された値に関する検証はviewに書かない。** ModelFormが担当する(Form Rules/Validation Rules参照)。重複チェックはモデルの制約から自動的に導かれるため、viewに`_validate_*`のようなヘルパーを作る必要はない。

viewに残る検証は、フォームを伴わない操作の事前条件だけである(「完了にする」「承認する」など)。その場合は書き込みヘルパーが`django.core.exceptions.ValidationError`を`code`付きで送出し、呼び出し側が受けて`messages.error()`に渡す。

`ValidationError`はフォーム専用ではなくDjango全体の検証例外であり、独自の例外階層を作る理由がないためこれを使う。文言は`error.messages[0]`で取り出す(`ValidationError`は複数の文言を保持できるため、属性は`message`ではなく`messages`になる)。

### modelとの役割分担

viewが持つのは操作の手順であり、状態の意味ではない。

- 「このオブジェクトが今どういう状態か」の判定はmodelに置く(`task.can_complete()`)。テンプレートから`{% if task.can_complete %}`と呼べるのもmodel側にある場合のみ
- 「その状態でこの操作をしてよいか」の判断と、実際の手順はviewに置く

判定ロジックをviewに書くとviewだけが太り、modelが空になる。判定はmodelへ、手順はviewへ寄せる。

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
# app/views/task.py
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from app.models import Task


# タスク完了
@login_required
def complete(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        return _complete_task(request, task)
    return render(request, 'app/task/complete.html', {'task': task})


# ============================================================
# ここから先はprivateヘルパー
# ============================================================


# タスクの完了処理を行う
def _complete_task(request, task):
    try:
        _apply_completion(task=task, operator=request.user)
    except ValidationError as error:
        messages.error(request, error.messages[0])
        return redirect('app:task_show', pk=task.pk)
    messages.success(request, 'タスクを完了しました。')
    return redirect('app:task_show', pk=task.pk)


# タスクを完了にする(履歴の作成を伴うためトランザクションにまとめる)
@transaction.atomic
def _apply_completion(*, task: Task, operator: User) -> Task:
    # 1. 検証(自身のstatusはModelのpureなメソッドで判定し、DBを参照する子タスクの状態はここで直接読む)
    if not task.can_complete():
        raise ValidationError('このタスクは完了にできません。', code='task_not_completable')
    if task.children.exclude(status=Task.Status.COMPLETED).exists():
        raise ValidationError('未完了の子タスクが残っています。', code='task_has_incomplete_children')

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

## Service Rules

`app/services/`は既定では作らない。書き込みはView Write Rulesに従いviewに置く。

次のいずれかに当てはまった時点で、はじめて`app/services/<model>.py`へ切り出す。

- **複数のviewから同じ業務操作を呼ぶ場合** — 一方のviewに置いて他方からimportすると、view同士が依存し合う
- **view以外の入口からも呼ぶ場合** — 管理コマンド、バッチ、外部API連携など。viewに置いた処理はHTTP経由でしか呼べない
- **複数モデルにまたがる大きなユースケース** — 1つのviewのprivateヘルパー群に収まらず、手順そのものに名前を付けたい規模になった場合

切り出す場合の書き方はView Write Rulesの書き込みヘルパーと同じ(キーワード専用引数、`HttpRequest`を受け取らない、`@transaction.atomic`、検証→変更→記録→通知の順、`ValidationError`の送出)。`app/services/<model>.py`に関数として定義し、`__init__.py`では`views/`と同様にモジュール単位でインポートして`services.<model>.<関数名>`の形で参照する。

**逆に、1つのviewからしか呼ばれない状態が続くserviceはviewへ戻す。** 呼び出し元が1箇所しかない層は、追跡の手間を増やすだけで何も守っていない。

## Read Rules

**viewからの読み取りはDjango本来の位置で行う。** 独自のselector層は作らない。

- **単一取得**: viewで`get_object_or_404(Model, pk=pk)`を直接呼ぶ。`Http404`はHTTPの関心事であり、modelには置かない
- **一覧取得**: `Model.objects.all()`、または繰り返し使う絞り込み・関連の先読みがある場合はカスタムQuerySetのメソッドを呼ぶ(QuerySet Rules参照)。ページネーション等の都合があるため、viewは評価前の`QuerySet`を受け取る
- **権限スコープによる絞り込み**: QuerySetのカスタムメソッド(`owned_by`等)に寄せ、viewは`get_object_or_404(Task.objects.owned_by(request.user), pk=pk)`のように渡すだけにする
- **404にするのは「存在しない/権限のスコープ外」だけ**: 「存在はするが今は編集できない」のような業務ルールによる操作不可は404にせず、書き込みヘルパーが`ValidationError`を送出する(View Write Rules参照)。混同するとURLを直接叩いた場合の挙動(404かエラーメッセージか)が食い違う

### Example

```python
# app/views/task.py
from django.shortcuts import get_object_or_404


@login_required
def index(request: HttpRequest) -> HttpResponse:
    tasks_qs = Task.objects.with_details()
    paginator = Paginator(tasks_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'app/task/index.html', {'tasks': page_obj, 'page_obj': page_obj})


# 編集対象のタスクを取得する(担当者以外には404)
@login_required
def edit(request: HttpRequest, pk: int) -> HttpResponse:
    task = get_object_or_404(Task.objects.assigned_to(request.user), pk=pk)
    ...
```

## QuerySet Rules

繰り返し使う絞り込み条件は、viewに直接書かず、カスタムQuerySetのメソッドとして定義する。同じ`filter()`が複数箇所に散ることを防ぎ、条件に業務上の名前を与えるため。

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
