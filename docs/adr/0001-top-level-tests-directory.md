# ADR-0001: テストコードをアプリの外のトップレベル tests/ に置く

Status: Accepted
Date: 2026-09-23

## 背景

テストは Django の既定どおりアプリの中(`app/tests/`)に置いていた。今後 `config` などアプリの外のコードにテストが必要になると、`config/tests/` のようにテストが各所に散らばり、テストコードの全体を掴みにくくなる。

## 決定

テストコードはプロジェクト直下の `tests/` にまとめ、ソース側のトップレベルディレクトリと同じ名前で分ける(`tests/app/models/` など)。E2E は `tests/e2e/` に置く。詳細は `.claude/instructions.md` の File Structure Rules。

## 却下した案

- アプリの中に置く(`app/tests/`。テンプレートの元方針)
  → アプリの外のコードのテストが各所に散らばり、テストコードの全体を掴みにくい。このプロジェクトの `app` は他のプロジェクトへの持ち出しを想定しておらず、アプリにテストを同梱する利点が小さい
- 層を先に分ける(`tests/unit/app/models/`)
  → `config` などのテストを、`tests/config/` のようにソースと同じ名前で置けない
- E2E をアプリの下に置く(`tests/app/e2e/`)
  → E2E の画面は複数のアプリにまたがり、特定のアプリに属さない
- `unit` を挟む(`tests/app/unit/models/`)
  → E2E がアプリの外に出たため `tests/app/` の中はユニットテストだけになり、`unit` は区別の役に立たない

## 影響

`app/tests/` を `tests/` へ移動(`app/tests/unit/<層>/` → `tests/app/<層>/`、`app/tests/e2e/` → `tests/e2e/`、`app/tests/conftest.py` → `tests/conftest.py`)。`tests/__init__.py` は、`tests/app/` が本物の `app` パッケージと同じ名前で読み込まれるのを防ぐために必須。

更新したファイル: `pyproject.toml`(`testpaths`、mypy の overrides)、`CLAUDE.md`、`README.md`、`docs/testing.md`、`.claude/instructions.md`(File Structure Rules、Test Layer Rules の例)、`tests/e2e/conftest.py`(コメント中のパス)。ユニットテストだけを実行するコマンドは `pytest --ignore=tests/e2e` になる。
