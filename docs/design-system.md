# 管理画面 デザインシステム(ダッシュボード・ブルー)

Task Manager 管理画面(タスク・社員・会社・部門・管理グループ)のUIルール。
淡いグレーの背景に白いカードを載せ、左サイドバーと青のアクセントで構成するダッシュボード調のデザイン。
参考にしたスクリーンショットから色・寸法・部品を実測して定義している(スクリーンショット自体はリポジトリに含めない)。

- **実装状況**: アプリ本体に適用済み。CSSは `app/static/app/common.css`(BootstrapのCSSは読み込まない。JSはモーダルの開閉にだけ使う)、シェルは `layouts/default.html` + `common/_sidebar.html` + `common/_topbar.html`、ログイン画面は `layouts/auth.html`。見本HTMLは同じCSSを直接読み込む。

## 「このデザインで」と指示されたら(AIエージェント向け)

**実際のCSSとHTMLの見本を正とし、本ドキュメントは値・ルールの補足として使う。** 見た目に迷ったら、まず見本を開く。

| ファイル | 内容 |
|---|---|
| [`component-catalog.md`](component-catalog.md) | 作成済みUIコンポーネントの一覧。**部品を探すときは最初にここを見る** |
| [`app/static/app/common.css`](../app/static/app/common.css) | 全トークン(`--ds-*`)と全コンポーネントのクラス(`ds-*`)の実装。**クラス名・値はここが唯一の正** |
| [`design-system/index.html`](design-system/index.html) | トップページの見本(カードを並べるダッシュボード構成・ドーナツチャート・凡例) |
| [`design-system/list.html`](design-system/list.html) | 一覧画面の見本(フラッシュメッセージ・ページヘッダー・テーブル・ステータス表示・空状態) |
| [`design-system/detail.html`](design-system/detail.html) | 詳細画面の見本(アクション3種・項目リスト) |
| [`design-system/form.html`](design-system/form.html) | フォーム画面の見本(入力・エラー表示・送信ボタン) |
| [`design-system/modal.html`](design-system/modal.html) | モーダルの見本(削除確認・短いフォーム。詳細画面の上で開く) |

ルール:

1. 新しい画面は、見本のマークアップと `common.css` の `ds-*` クラスだけで組み立てる。Bootstrapのクラスや独自のインラインスタイル、新しい色・影・角丸・フォントサイズは足さない(例外: チャートの割合を表す `conic-gradient` のみインライン指定。Bootstrap の JS で動かす部品では、JS が要求するクラス(モーダルの `modal` `fade` `modal-dialog` など)を `ds-*` と併記する)。
2. 画面の種類(トップ/一覧/詳細/フォーム)に対応する見本を選び、そのHTML構造をそのままテンプレートに写す。サイドバー+トップバーのシェルは全画面で共通。Djangoのテンプレートタグは見本の文言・値の部分だけに使う。
3. カタログ・見本にない部品が必要なときは、下の「UIコンポーネントを追加するとき」の手順に従う。見本に追加してユーザーの承認を得るまで、アプリの画面では使わない。
4. 見本はブラウザで開ける。CSSを `../../app/static/app/common.css` で参照しているため、リポジトリのルートで `python3 -m http.server` を起動し、`/docs/design-system/list.html` などを開く。
5. テストが依存するフック(`id` 属性、フラッシュメッセージの `.messages`、行の `.<model>-row` など)は、デザインを変えても残す。

### UIコンポーネントを追加するとき

モーダル・ドロップダウン・タブのような部品が必要になったら、次の順に探す。

1. **カタログを見る。** [`component-catalog.md`](component-catalog.md) にあれば、それをそのまま使う(新しく作らない)。足りない機能があるときは、その部品を拡張する形で 2〜3 の手順に進む。
2. **カタログになければ、Bootstrap 5(`static/vendor/bootstrap/` の同梱版、v5.3.3)に同じ機能があるか確認する。** ある場合は Bootstrap の仕組みを使う。
   - 開閉などの動きは `bootstrap.bundle.min.js` と `data-bs-*` 属性に任せ、同じ動きを自前で書かない。
   - Bootstrap の CSS は読み込まない。見た目は `common.css` に `ds-*` クラスとして定義し、JS が要求するクラスは `ds-*` と併記する。
   - サイズなどのバリエーションは Bootstrap の段階と値に合わせる(例: モーダルの幅 `--sm` / 標準 / `--lg` / `--xl`)。
3. **Bootstrap にもなければ、自前で作って提案する。**
   - Bootstrap の部品で足りない部分(例: モーダルのドラッグ移動)も含む。
   - スクリプトは `app/static/app/<部品名>.js`、見た目は `common.css` に置く。
   - ユーザーには、カタログと Bootstrap に無いことを確認した旨と、作ったものを報告する。
4. **2・3 のどちらの場合も、`common.css`・見本HTML・本ドキュメントに追加し、カタログに1行追加する。** ユーザーが見本で確認して承認してから画面に使う。

主なクラス: `ds-page`(body) / `ds-app` `ds-sidebar` `ds-brand` `ds-nav-label` `ds-nav-item` `ds-topbar` `ds-user` `ds-avatar` `ds-main` `ds-content` / `ds-icon ds-icon--*` / `ds-page-header` `ds-h1` `ds-actions` / `ds-card` (+ `--flush` `--narrow`) `ds-card-header` `ds-card-title` / `ds-grid` (+ `--main-side`) / `ds-btn` + `ds-btn-primary|danger` (+ `ds-btn-sm`) / `ds-status` (+ `--progress|--done|--danger`) / `ds-alert` + `--success|--error` `ds-empty` / `ds-form` `ds-field` `ds-label` `ds-input` (+ `--error`) `ds-field-error` / `ds-table` / `ds-detail*` / `ds-modal` `ds-modal-dialog` (+ `--sm` `--lg` `--xl`) `ds-modal-content` `ds-modal-header` `ds-modal-title` `ds-modal-close` `ds-modal-body` `ds-modal-footer` / `ds-donut*` `ds-legend`

## 原則

1. 背景は淡いグレー、コンテンツは白いカード(角丸12px・影なし)に載せる。区切りは余白と極薄の罫線だけで行う。
2. アクセントは青(`--ds-primary`)1色。現在地・主要ボタン・進行中を青で示し、状態の意味色(緑/黄/赤)はステータスのドットとアラートにだけ使う。
3. 文字は黒(本文)とネイビー(ナビ)、補助は青みのグレー。装飾のための色は足さない。

## 1. カラー

| トークン | HEX | 用途 |
|---|---|---|
| `--ds-primary` | `#4062e1` | 主要ボタン、ナビの現在地、リンク、フォーカス、進行中 |
| `--ds-primary-hover` | `#3553c8` | primaryボタンのホバー |
| `--ds-primary-tint` | `#f0f3fd` | ナビ項目のホバー背景 |
| `--ds-navy` | `#192649` | サイドバーの文字・アイコン |
| `--ds-ink` | `#0a0b10` | 本文・タイトル・表の値 |
| `--ds-text-2` | `#454c60` | 凡例・チャート中心のラベルなど二次テキスト |
| `--ds-muted` | `#6f778a` | 表ヘッダー、詳細の項目名、日時などの補助 |
| `--ds-label` | `#8b92ad` | サイドバーのセクション見出し(装飾用の小さな文字。本文に使わない) |
| `--ds-bg` | `#f6f7f9` | ページ背景 |
| `--ds-surface` | `#ffffff` | カード・サイドバー・トップバー・入力欄 |
| `--ds-line` | `#f1f2f6` | 表ヘッダーの罫線、詳細の項目区切り |
| `--ds-secondary` / `-hover` | `#e9ecf7` / `#dfe3f2` | secondaryボタンの塗りとホバー |
| `--ds-border-button` | `#c3c8d6` | secondaryボタンの罫線 |
| `--ds-border-control` | `#d9dce6` | 入力欄の罫線、空状態の点線 |
| `--ds-hover` | `#f9fafd` | 表の行ホバー |
| `--ds-success` / `-halo` | `#89b33b` / `#eef7d0` | Done のドットと外周 |
| `--ds-warning` / `-halo` | `#d5a648` / `#f7efe4` | To Do のドットと外周 |
| `--ds-info` / `-halo` | `#4062e1` / `#e3e9fb` | In Progress のドットと外周、アバター背景 |
| `--ds-danger` / `-hover` / `-halo` | `#cb3b2a` / `#b2301f` / `#f4e2e3` | 削除ボタン、入力エラー、危険ステータス |
| `--ds-success-*` / `--ds-danger-*`(bg, border, text) | 見本CSS参照 | アラートの背景・罫線・文字 |
| `--ds-chart-1/2/3` | `#1c3d63` `#4062e1` `#71adf8` | チャートと凡例(この順で使う) |

`--ds-notify`(`#ec5437`)は通知バッジ用に定義しているが、現状の見本では使っていない。

## 2. タイポグラフィ

フォント: `"BIZ UDPGothic"`(英数字・日本語とも。Google Fonts、400/700のみ)、フォールバック `system-ui, sans-serif`。500は400、600は700で表示される。
**サイズは Bootstrap 5 の標準スケール(rem)に合わせる**(`html` の基準は16px)。

| トークン | サイズ | Bootstrap 対応 | 太さ | 用途 |
|---|---|---|---|---|
| `--ds-fs-xs` | 0.75rem (12px) | badge 相当 | 600 | サイドバーのセクション見出し(letter-spacing 0.15em) |
| `--ds-fs-sm` | 0.875rem (14px) | `small` | 400/700 | 表ヘッダー、詳細の項目名、エラーメッセージ、小ボタン、アバター |
| `--ds-fs-base` | 1rem (16px) | body | 400/500 | 本文、ナビ項目、表の値、ボタン、入力欄、ラベル |
| `--ds-fs-h5` | 1.25rem (20px) | `h5` | 600 | カードタイトル、ブランド名 |
| `--ds-fs-h4` | 1.5rem (24px) | `h4` | — | (定義のみ) |
| `--ds-fs-h3` | 1.75rem (28px) | `h3` | 600 | ページタイトル(`ds-h1`)、チャート中心の数値 |

line-height は 1.5(Bootstrap 標準)。太さは、ナビ・ボタン・表の値が 500、タイトルが 600、ブランドが 700。

## 3. スペーシング・形状

- ページ余白 30px、カード間 30px(`ds-grid` の gap)。カード内 padding 24px(ヘッダーは `20px 24px`)。
- サイドバー幅 256px、トップバー高 64px。
- ナビ項目: 高さ44px、左右padding 14px、アイコン20px+gap 12px、項目間 4px、角丸10px。
- ボタン・入力欄: padding `8px 16px`(小ボタン `4px 12px`)、角丸8px。カード・空状態は角丸12px。
- 表: ヘッダー `14px 24px`、行 `12px 24px`(1行48px)。
- 影は使わない(フォーカスリング `0 0 0 3px rgba(64,98,225,.22)` のみ)。

## 4. コンポーネント

### アプリシェル

左に白いサイドバー(ブランド → 「メニュー」見出し → ナビ項目、最下部にログアウト)、右にトップバー(右寄せのユーザー表示)とコンテンツ領域。
現在ページのナビ項目は `aria-current="page"` を付け、青の塗り+白文字にする。ログアウトはPOSTフォームの `button.ds-nav-item`。ユーザーはイニシャルのアバター(36px円、`info-halo` 背景)+名前(管理者は「(管理者)」付記)。

### ボタン

| 種別 | クラス | 用途 |
|---|---|---|
| primary | `ds-btn ds-btn-primary` | 保存・編集・新規作成(青塗り、白文字) |
| secondary | `ds-btn` | 戻る・キャンセル・「すべて見る」(薄い青灰色の塗り `--ds-secondary`、文字 `--ds-navy`、罫線 `--ds-border-button` 1px。影なし) |
| danger | `ds-btn ds-btn-danger` | 削除(赤塗り、白文字) |
| small | `ds-btn-sm` を併記 | カードヘッダー内などの小さな操作 |

並べるときは gap 8、secondary → primary → danger の順。1画面の主アクション(primary)は1つ。
secondary を白抜きにしないのは、青・赤の塗りつぶしボタンと並べたとき、白い面が小さく低く見えるため(実測の高さは同じ42px)。塗りと、背景より濃い罫線で面の大きさをそろえる。

### ステータス表示

10pxのドットに、5pxの淡い外周(ハロー)を付け、右に文言を置く(`ds-status`)。To Do=黄(既定)、In Progress=青(`--progress`)、Done=緑(`--done`)、`--danger`=赤(現状のタスクでは未使用)。文言は必ず併記する。

### アラート

角丸8px、padding `12px 16px`、罫線1px、20pxのアイコン+文言。成功フラッシュ(緑、閉じる×付き。文言は「{モデル名}を{作成/更新/削除}しました。」)、フォーム全体エラー(赤、閉じるなし)、空状態(`ds-empty`: 白・点線・中央寄せ。例「タスクがありません。」)。

### フォーム

白いカード(`ds-card ds-card--narrow`)の中に `ds-form` を置く。ラベルは入力欄の上(16px/500、間隔8px)、項目間20px。入力欄は白背景・罫線 `border-control`・角丸8px。フォーカスは罫線を primary にしてリング。エラーは `ds-input--error`(赤罫線)+直下の `ds-field-error`(14px、赤。例: 「説明には関連するIssue番号(例: #123)を含めてください。」)。送信は primary「保存」+secondary「キャンセル」。

### 一覧テーブル

`ds-card ds-card--flush` の中に `ds-table` を置く(カードの縁まで表を広げる)。ヘッダーは14px・`muted`・上下に極薄の罫線。行は罫線なし、ホバーで `hover` 背景、行全体がクリック可能(`data-href`)。タイトルなどの値は 500、日時・数値は `muted`。カードにタイトルが必要なときは `ds-card-header` を表の上に置く。

### 詳細表示

`ds-card ds-card--flush` の中に `ds-detail`(dl)。項目名(14px、`muted`、コロンなし)の下に値(500)を積み、項目間を `line` の罫線で区切る。値が空のときは「なし」「未割り当て」など。

### モーダル

開閉は Bootstrap 5 の modal.js(`static/vendor/bootstrap/js/bootstrap.bundle.min.js`)に任せ、開閉の動き(上から滑り込むフェード、Escキー・背景クリックで閉じる、フォーカスの閉じ込め、背面スクロールの停止)を Bootstrap と同じにする。Bootstrap の CSS は読み込まないので、見た目は `common.css` の `ds-modal*` で定義している。白いパネル(幅は下表、画面上部から30px、角丸12px、影なし)を、`ink` を45%の不透明度にした背景に重ねる。

- マークアップ: `div.modal.fade.ds-modal`(`tabindex="-1"`、`aria-labelledby` でタイトルに結び付ける)> `div.modal-dialog.ds-modal-dialog` > `form.ds-modal-content` > `ds-modal-header`(`ds-modal-title` の h2 + 右端の × `ds-modal-close`)→ `ds-modal-body` → `ds-modal-footer`(右寄せ、上に `line` の罫線)。
- `modal` `fade` `modal-dialog` は Bootstrap の JS が探すクラスなので、`ds-*` と併記する(見た目は付かない)。背景として Bootstrap が生成する `modal-backdrop` だけは、`common.css` でそのクラス名のまま見た目を定義している。
- 開くボタンは `<button type="button" data-bs-toggle="modal" data-bs-target="#<id>">`。× とキャンセルは `<button type="button" data-bs-dismiss="modal">` にして、送信せずに閉じる。開閉のために独自のスクリプトは書かない。
- 幅は `ds-modal-dialog` に修飾クラスを併記して変える(値は Bootstrap の `modal-sm` / 標準 / `modal-lg` / `modal-xl` と同じ)。画面が狭いときは画面幅に合わせて縮む。

  | クラス | 最大幅 | 目安 |
  |---|---|---|
  | `ds-modal-dialog--sm` | 300px | 1文だけの確認 |
  | (無指定) | 500px | 確認・短いフォーム(既定) |
  | `ds-modal-dialog--lg` | 800px | 表や長めの本文を見せる |
  | `ds-modal-dialog--xl` | 1140px | 一覧を丸ごと見せる |

- ヘッダー(`ds-modal-header`)をドラッグするとモーダルを移動できる(`app/static/app/modal.js`、カーソルは移動の形)。× ボタンの上ではドラッグしない。ヘッダーが画面の外に出ない範囲で動かせ、閉じると元の位置に戻る。
- フッターのボタン順はページと同じく secondary「キャンセル」→ primary/danger。

| 種類 | 用途 | 中身 |
|---|---|---|
| 確認 | 削除など取り消せない操作の最終確認 | 本文は1〜2文(例「「資料作成」を削除します。この操作は取り消せません。」)。実行ボタンは danger |
| フォーム | 1〜3項目の短い入力(ステータス変更など) | 本文に `ds-form` を置く。エラー表示はフォーム画面と同じ。項目がそれ以上になる場合はモーダルにせずフォーム画面にする |

モーダルを重ねて開かない。成功時の結果は、これまでどおり送信後のリダイレクト先でフラッシュメッセージとして表示する。`bootstrap.bundle.min.js` は `layouts/default.html` で全画面に読み込んでいる。`app/modal.js` はモーダルの無い画面に読み込まないよう、モーダルを置く画面のテンプレートで `{% block extra_js %}` に読み込む(モーダルを条件付きで出す場合は、同じ条件で囲む)。使用例: タスク詳細画面のステータス変更(`app/templates/app/task/show.html`)。

### ページヘッダー

コンテンツの先頭に、左へ h1(`ds-h1`、28px/600)、右へアクション群。下のカードとの間隔は24px。

### ドーナツチャート・凡例(ダッシュボード用)

カード内に `ds-donut`(180px、リング幅22px、中心に合計値)+`ds-legend`(ドット+ラベル+右寄せの件数)。色は `--ds-chart-1/2/3` をこの順に使う。ダッシュボード用のカード構成(`ds-grid--main-side`)は、対応する機能があるときだけ使う。

## 5. 参考デザインから採用しなかった要素

検索ボックス、通知ベル、ダークモード切替、写真付きカード・カルーセル・地図、価格タグなどは、Task Manager に対応する機能がないため見本に含めていない。必要になった場合は、ユーザーに確認してから `common.css` に追加する。

## 6. 実装との対応

- 共通部: `app/templates/layouts/default.html`(サイドバー+トップバー+コンテンツ)、`layouts/auth.html`(ログイン用の中央寄せ)、`common/_sidebar.html`、`common/_topbar.html`、`common/_messages.html`
- 各モデルの画面: `app/templates/app/<model>/{index,show,new,edit,delete,_form}.html`。フォームのウィジェットは `app/forms/*.py` で `ds-input` / `ds-check` を指定する。
- 現在ページのナビ項目は、`request.resolver_match.url_name` に基づいて `_sidebar.html` が `aria-current="page"` を付ける(新しいモデルを追加したらナビ項目も追加する)。
- 見本にない画面(削除確認・ログイン・403・トップ)は、既存のクラスの組み合わせで作っている: 削除確認は `ds-card--narrow` + `ds-stack` + `ds-actions`(危険ボタン+キャンセル)、トップは `ds-card--narrow` + `ds-stack`、チェックボックスは `ds-field ds-field--check` + `ds-check`。
- モデル別CSS(`app/static/app/<model>.css`)は行の `cursor: pointer` のみで、`ds-table` の `tr[data-href]` と重複しているが、CSS Rules(instructions.md)に従い残している。

新しい画面を実装・レビューするAIエージェントは、まず本ファイルと見本を確認し、ここにないパターンが必要な場合はユーザーに確認してから追加すること。
