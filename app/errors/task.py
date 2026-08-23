from app.errors.base import DomainError


# 説明に関連するIssue番号(#から始まる文字列)が含まれていない
class TaskDescriptionMissingIssueReferenceError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            code='task_description_missing_issue_reference',
            message='説明には関連するIssue番号(例: #123)を含めてください。',
        )
