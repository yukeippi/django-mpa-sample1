from dataclasses import dataclass, field
from typing import Any


# messageは画面表示用の日本語文言。codeとparamsは現時点でアプリ内では未使用だが、
# 将来Datadog等へ構造化ログとして送る際に、code(英語の識別子)をログメッセージ、
# paramsを検索・集計可能なフィールドとして使う想定であえて残している
@dataclass(eq=False)
class DomainError(Exception):
    code: str
    message: str
    params: dict[str, Any] = field(default_factory=dict)
