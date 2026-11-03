# ADR-0003: 仕様の箇条書きを docs/spec/ に当時の記録として積む

Status: Accepted
Date: 2026-09-25

## 背景

Test-First Rules では、テストを書く前に作る仕様の箇条書きを `tmp/spec/` に置き、Git で追跡しないことにしていた。社員の所属部門の割り当て機能を実装した際、この箇条書きが分かりやすく、保存したほうが良いと判断した。

## 決定

仕様の箇条書きは `docs/spec/<作成日時>-<機能名>.md` に置き、Git で追跡する。各ファイルの冒頭に「作成時点の記録であり、現在の挙動の正本はコードとテスト」と書き、完了後は更新しない。詳細は `.claude/instructions.md` の Test-First Rules。

## 却下した案

- `tmp/spec/` に置き、Git で追跡しない(テンプレートの元方針)
  → 箇条書きの仕様が分かりやすく、保存したほうが良い
- `docs/spec/` の仕様を、現在の仕様として保守する(挙動を変えるたびに更新する)
  → 現在の仕様書は、いずれ GitHub Wiki に積み上げたいと考えているため

## 影響

`.claude/instructions.md` の Test-First Rules(「仕様の箇条書きをどこに書くか」を `docs/spec/` に変更し、末尾に `経緯: ADR-0003`)を更新。`tmp/spec/` にあった仕様3件を `docs/spec/` に移し、冒頭に記録である旨を追記した。

- `docs/spec/202609230905-task-status.md`
- `docs/spec/202609231121-task-detail-pane.md`
- `docs/spec/202609250035-employee-department.md`
