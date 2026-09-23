# UIコンポーネントカタログ

このアプリで作成済みのUIコンポーネントの一覧。画面やUI部品を作るときは、**最初にこのカタログを見る**。ここにある部品は、新しく作らずにそのまま使う。

- ここにない部品が必要なときは、[design-system.md](design-system.md) の「UIコンポーネントを追加するとき」の手順(Bootstrap を確認 → なければ作って提案)に従う。
- 部品を追加・変更したら、このカタログも更新する。
- 見た目の値・細かいルールは design-system.md の「4. コンポーネント」、クラスの実装は `app/static/app/common.css` が正。

「作り」の列の意味:

- **自前**: `common.css` のCSSだけで作った部品
- **Bootstrap**: 動きは Bootstrap 5 の JS(`static/vendor/bootstrap/js/bootstrap.bundle.min.js`)、見た目は `common.css`
- **Bootstrap+自前**: Bootstrap の部品に、自前のスクリプトで機能を足したもの

| 部品 | 用途 | 作り | 主なクラス・属性 | 見本 | 仕様 |
|---|---|---|---|---|---|
| アプリシェル | 全画面共通の枠(サイドバー+トップバー+コンテンツ) | 自前 | `ds-app` `ds-sidebar` `ds-nav-item` `ds-topbar` `ds-user` `ds-avatar` `ds-main` `ds-content` | すべての見本 | [アプリシェル](design-system.md#アプリシェル) |
| ページヘッダー | ページタイトルと右寄せのアクション | 自前 | `ds-page-header` `ds-h1` `ds-actions` | [list.html](design-system/list.html) | [ページヘッダー](design-system.md#ページヘッダー) |
| カード | 白い面にコンテンツを載せる | 自前 | `ds-card`(+ `--flush` `--narrow`) `ds-card-header` `ds-card-title` | [index.html](design-system/index.html) | [原則](design-system.md#原則) |
| レイアウト | カードを並べる・縦に積む | 自前 | `ds-grid`(+ `--main-side`) `ds-stack` | [index.html](design-system/index.html) | [実装との対応](design-system.md#6-実装との対応) |
| アイコン | ナビ・ボタンのアイコン | 自前 | `ds-icon ds-icon--<名前>`(home, tasks, users, building, sitemap, shield, logout, login, check) | すべての見本 | `common.css` の `--ds-icon-*` |
| ボタン | 操作(primary / secondary / danger、小サイズ) | 自前 | `ds-btn`(+ `ds-btn-primary` `ds-btn-danger` `ds-btn-sm`) | [detail.html](design-system/detail.html) | [ボタン](design-system.md#ボタン) |
| ステータス表示 | タスクの状態をドット+文言で示す | 自前 | `ds-status`(+ `--progress` `--done` `--danger`) | [list.html](design-system/list.html) | [ステータス表示](design-system.md#ステータス表示) |
| アラート | 成功のフラッシュ、フォーム全体のエラー | 自前 | `ds-alert`(+ `--success` `--error`) `ds-alert-message` `ds-alert-close` `ds-messages` | [list.html](design-system/list.html) / [form.html](design-system/form.html) | [アラート](design-system.md#アラート) |
| 空状態 | 一覧が0件のときの表示 | 自前 | `ds-empty` | [list.html](design-system/list.html) | [アラート](design-system.md#アラート) |
| フォーム | 入力欄・セレクト・チェックボックス・項目エラー | 自前 | `ds-form` `ds-field`(+ `--check`) `ds-label` `ds-input`(+ `--error`) `ds-check` `ds-field-error` `ds-form-actions` | [form.html](design-system/form.html) | [フォーム](design-system.md#フォーム) |
| 一覧テーブル | レコードの一覧(行クリックで詳細へ) | 自前 | `ds-table`、行に `data-href` | [list.html](design-system/list.html) | [一覧テーブル](design-system.md#一覧テーブル) |
| 詳細表示 | 1レコードの項目名と値 | 自前 | `ds-detail` `ds-detail-item` `ds-detail-label` `ds-detail-value` | [detail.html](design-system/detail.html) | [詳細表示](design-system.md#詳細表示) |
| ドーナツチャート・凡例 | ダッシュボードの割合表示 | 自前 | `ds-donut` `ds-donut-chart` `ds-donut-center` `ds-legend` | [index.html](design-system/index.html) | [ドーナツチャート・凡例](design-system.md#ドーナツチャート・凡例ダッシュボード用) |
| ログイン画面の枠 | 未ログイン画面の中央寄せカード | 自前 | `ds-auth` `ds-auth-card` | なし(`layouts/auth.html`) | [実装との対応](design-system.md#6-実装との対応) |
| 右ペイン | 一覧の行から、画面を移動せずに詳細を右側に表示する | Bootstrap | `offcanvas offcanvas-end ds-offcanvas` > `ds-offcanvas-header` / `ds-offcanvas-body` / `ds-offcanvas-footer`、開く `data-bs-toggle="offcanvas"`、閉じる `data-bs-dismiss="offcanvas"` | [offcanvas.html](design-system/offcanvas.html) | [右ペイン](design-system.md#右ペイン) |
| モーダル | 確認(削除など)・短いフォーム。幅4段階、ヘッダーのドラッグで移動 | Bootstrap+自前 | `modal fade ds-modal` > `modal-dialog ds-modal-dialog`(+ `--sm` `--lg` `--xl`) > `ds-modal-content`、開く `data-bs-toggle="modal"`、閉じる `data-bs-dismiss="modal"`。ドラッグは `app/static/app/modal.js` | [modal.html](design-system/modal.html) | [モーダル](design-system.md#モーダル) |
