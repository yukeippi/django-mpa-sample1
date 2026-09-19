# 管理画面 デザインシステム(モノクロ・ミニマル)

Task Manager 管理画面(タスク・社員・会社・部門・管理グループ)のUIルール。
罫線と余白で情報を整理し、色は最小限に抑える。新しい画面・コンポーネントは、ここに定義したトークンとパターンだけで組み立てること。

- 視覚的なリファレンス(実物の見た目・検討案含む): https://claude.ai/artifact/Uif1FsLkyu4ofxNUpCdtP8
- **実装状況**: アプリ本体には未反映。現行のテンプレート/CSSは Bootstrap 5.3.3 の既定スタイルのまま。本ドキュメントは移行後の目標仕様。

## 「このデザインで」と指示されたら(AIエージェント向け)

**実際のCSSとHTMLの見本を正とし、本ドキュメントは値・ルールの補足として使う。** 見た目に迷ったら、まず見本を開く。

| ファイル | 内容 |
|---|---|
| [`design-system/theme.css`](design-system/theme.css) | 全トークン(`--ds-*`)と全コンポーネントのクラス(`ds-*`)の実装。**クラス名・値はここが唯一の正** |
| [`design-system/index.html`](design-system/index.html) | トップページの見本 |
| [`design-system/list.html`](design-system/list.html) | 一覧画面の見本(フラッシュメッセージ・ページヘッダー・テーブル・ステータス表示・空状態) |
| [`design-system/detail.html`](design-system/detail.html) | 詳細画面の見本(アクション3種・項目リスト) |
| [`design-system/form.html`](design-system/form.html) | フォーム画面の見本(入力・エラー表示・送信ボタン) |

ルール:

1. 新しい画面は、見本のマークアップと `theme.css` の `ds-*` クラスだけで組み立てる。Bootstrapのクラスや独自のインラインスタイル、新しい色・影・角丸は足さない。
2. 画面の種類(一覧/詳細/フォーム/トップ)に対応する見本を選び、そのHTML構造をそのままテンプレートに写す(Djangoのテンプレートタグは見本の文言・値の部分だけに使う)。
3. 見本にないパターンが必要なときは、勝手に作らずユーザーに確認する。承認されたら `theme.css` と見本HTMLに追加してから使う。
4. 見本はブラウザで直接開ける(`design-system/list.html` などをダブルクリック)。

主なクラス: `ds-page`(body) / `ds-nav*` / `ds-container` / `ds-page-header` / `ds-actions` / `ds-h1` / `ds-display` / `ds-btn` + `ds-btn-primary|secondary|danger` (+ `ds-btn-sm`) / `ds-status` (+ `--progress|--done`) / `ds-alert` + `--success|--error` / `ds-empty` / `ds-form` `ds-field` `ds-label` `ds-input` (+ `--error`) `ds-field-error` / `ds-table-wrap` `ds-table` / `ds-detail*`

## アプリ本体への反映方針(未着手)

`theme.css` を `app/static/app/` に取り込み、`layouts/default.html` から読み込んで、各テンプレートのBootstrapクラスを `ds-*` に置き換える。置き換え対象は `app/templates/` 配下(navbar・messages・各モデルの index/show/_form)と、`app/forms/*.py` のウィジェットの `class` 属性(`form-control` / `form-select` → `ds-input`)。

## 原則

1. 面の塗り分けや影ではなく、1pxの罫線と十分な余白でグルーピングする。
2. 色はアクセント1色(スレートブルー)+意味色(赤)のみ。赤は削除・エラーにしか使わない。
3. 装飾を足さない: 影・グラデーション・塗りつぶしバッジ・縞模様・アイコンの飾り使いは禁止。

## 1. カラー

| トークン | oklch | HEX | 用途 |
|---|---|---|---|
| `--ds-ink` | `oklch(20% 0.005 260)` | `#151618` | 本文、primaryボタン背景 |
| `--ds-ink-hover` | `oklch(15% 0.005 260)` | `#0a0b0d` | primaryボタンのホバー |
| `--ds-muted` | `oklch(45% 0.01 260)` | `#52555b` | 補助テキスト、表ヘッダー、数値・日時 |
| `--ds-accent` | `oklch(45% 0.05 250)` | `#405870` | リンク、進行中ドット、フォーカス、ナビの現在地 |
| `--ds-accent-tint` | `oklch(94% 0.015 250)` | `#e4ecf5` | 成功フラッシュの背景(罫線は `oklch(85% 0.03 250)`、文字は `oklch(30% 0.05 250)`) |
| `--ds-danger` | `oklch(50% 0.15 25)` | `#a83634` | 削除ボタンの文字・枠、入力エラーの枠とメッセージ |
| `--ds-danger-bg` | `oklch(96% 0.02 25)` | `#ffedeb` | エラーアラート背景・dangerボタンのホバー(罫線 `oklch(85% 0.06 25)`、文字 `oklch(42% 0.14 25)`) |
| `--ds-bg` | `oklch(98% 0.003 90)` | `#f9f8f6` | ページ背景 |
| `--ds-surface-subtle` | `oklch(96.5% 0.003 90)` | `#f4f3f1` | 表ヘッダー背景 |
| `--ds-hover` | `oklch(96% 0.003 90)` | `#f2f2ef` | 表の行ホバー |
| `--ds-border` | `oklch(90% 0.005 260)` | `#dcdee1` | 表・詳細・アラートなどコンテナの罫線 |
| `--ds-border-control` | `oklch(87% 0.005 260)` | `#d2d4d7` | 入力欄・ボタンの罫線 |
| `--ds-row-line` | `oklch(93% 0.004 90)` | `#e9e8e5` | 表の行区切り、詳細表示の項目区切り |
| `--ds-dot-idle` | `oklch(80% 0.005 260)` | `#bcbec1` | 未着手ステータスのドット |

入力欄の背景は白 `#fff`。フォーカスリングは `0 0 0 3px oklch(45% 0.05 250 / 0.25〜0.3)`(dangerのボタンは `oklch(50% 0.15 25 / 0.25)`)。これがこのシステムで唯一の box-shadow。

## 2. タイポグラフィ

フォント: `"Zen Kaku Gothic New"`(Google Fonts、400/500/700)、フォールバック `system-ui, sans-serif`。

| 名前 | サイズ/太さ | 用途 |
|---|---|---|
| display | 32px / 700 / line-height 1.25 | トップページの見出し |
| h1 | 24px / 700 | ページタイトル(1画面に1つ) |
| section | 16px / 700 | セクション見出し |
| body | 14px / 400 / line-height 1.6 | 本文・表のセル・入力値 |
| label | 13px / 500 | フォームのラベル |
| caption | 12px / 700 / letter-spacing 0.03em / `--ds-muted` | 表ヘッダー、詳細表示の項目名 |
| small | 12px / 400 / `--ds-muted` | 補足説明。エラーは `--ds-danger` |

## 3. スペーシング・角丸

- スペーシングは4pxベース: 4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48。
  - 8: ボタン同士、関連要素の間 / 16: フォーム項目間、ボタン左右padding / 20: 表セルの左右padding / 24: ページヘッダー下・コンポーネント間 / 48: ページ左右padding、セクション間
- 角丸: 4(小要素)/ 6(ボタン・入力欄)/ 8(表・詳細・アラート)。
- 影は使わない(フォーカスリング除く)。

## 4. コンポーネント

### ボタン

共通: 14px/500、padding `9px 16px`、角丸6。small(ナビ・表内)は 13px、padding `6px 12px`。

| 種別 | 用途 | 通常 | ホバー | フォーカス |
|---|---|---|---|---|
| primary | 保存・編集・新規作成 | 背景 `ink`、文字白 | 背景 `ink-hover` | 通常+フォーカスリング |
| secondary | 戻る・キャンセル | 背景なし、罫線 `border-control` | 背景 `oklch(94% 0.004 90)` | 罫線 `accent`+リング |
| danger | 削除 | 背景なし、文字と罫線(40%)が `danger` | 背景 `danger-bg` | 罫線 `danger`+リング |

- 1画面の primary は1つだけ。削除は塗りつぶさず枠線のみ。
- ボタンを並べるときは gap 8、secondary → primary の順。

### ステータス表示

塗りつぶしバッジは使わない。6pxのドット(または12pxのチェック)+文言を必ず併記する。

- To Do: `--ds-dot-idle` のドット / In Progress: `--ds-accent` のドット / Done: `--ds-ink` のチェックアイコン(stroke 1.8、SVG)

### アラート

角丸8、padding `12px 16px`、罫線1px、アイコン16px(SVG)+文言。

- 成功フラッシュ(閉じる×付き): `accent-tint` 背景。文言は「{モデル名}を{作成/更新/削除}しました。」
- フォーム全体エラー(閉じるなし): `danger-bg` 背景、danger 罫線・文字、円形の!アイコン
- 空状態: 背景なし、`1px dashed border-control`、中央寄せ、文字 `muted`。例「タスクがありません。」

### フォーム

- ラベルは入力欄の上、13px/500、ラベルと入力欄の間 6px、項目間 16px。カードで囲まず背景に直接置く。
- 入力欄(input/textarea/select): padding `9px 12px`、罫線 `border-control`、角丸6、背景白。selectは右端に chevron アイコン(14px、`muted`)。
- フォーカス: 罫線を `accent` にしてリング。
- エラー: 罫線を `danger` にし、入力欄の直下に 12px の `danger` 文字でメッセージ(例: 「説明には関連するIssue番号(例: #123)を含めてください。」)。
- 送信ボタン: primary「保存」、必要に応じて secondary「キャンセル」を右に並べる。

### 一覧テーブル

- コンテナ: `1px solid border`、角丸8、`overflow: hidden`。
- ヘッダー行: 背景 `surface-subtle`、caption スタイル、padding `12px 20px`、下罫線 `border`。
- データ行: padding `16px 20px`、行間は `row-line` の罫線(縞模様は使わない)。ホバーで背景 `hover`、行全体がクリック可能(`cursor: pointer`)。
- 数値・日時は `muted`。ステータスは上記のドット/チェック表示。

### 詳細表示

`1px solid border`・角丸8のコンテナ内に項目を縦積み。各項目 padding `16px 20px`、項目間は `row-line` の罫線。項目名は caption(コロンなし)、その下に body の値(空のときは「なし」「未割り当て」など)。

### ページヘッダー

左に h1、右にアクション群(flex、`justify-content: space-between`、`align-items: center`)。下のコンテンツとの間隔は24px。

### ナビゲーションバー

高さ56px、背景 `bg`、`1px solid border`(暗い帯は使わない)。左: ブランド名(15px/700)+リンク(14px/500、`muted`、gap 20)。現在ページは文字色 `ink` + 下に 2px の `accent` 線。右: ユーザー名(13px、`muted`、管理者は「(管理者)」付記)+small secondary の「ログアウト」。

### トップページ

塗りつぶしのヒーロー面は使わない。display 見出し + 15px の `muted` リード文 + ボタン(primary + secondary)を、上下48pxの余白で配置する。

## 5. 実装との対応(現状)

- 共通部: `app/templates/layouts/default.html`, `app/templates/common/_navbar.html`, `app/templates/common/_messages.html`
- 自前CSS: `app/static/app/common.css`、モデル別 `app/static/app/<model>.css`(行クリック用 `cursor: pointer` のみ)
- 各モデルの画面: `app/templates/app/<model>/{index,show,_form}.html`

新しい画面を実装・レビューするAIエージェントは、まず本ファイルを確認し、ここにないパターンが必要な場合はユーザーに確認してから追加すること。
