from django.core.exceptions import ValidationError


# 説明に関連するIssue番号(#から始まる文字列)が含まれていることを検証する
def validate_description_contains_issue_reference(value: str) -> None:
    if value and '#' not in value:
        raise ValidationError(
            '説明には関連するIssue番号(例: #123)を含めてください。',
            code='task_description_missing_issue_reference',
        )
