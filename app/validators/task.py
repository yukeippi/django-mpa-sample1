from app import errors


# 説明に関連するIssue番号(#から始まる文字列)が含まれていることを検証する。正しければそのまま返す
def validate_description_contains_issue_reference(value: str) -> str:
    if value and '#' not in value:
        raise errors.task.TaskDescriptionMissingIssueReferenceError()
    return value
