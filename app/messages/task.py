from app.errors.base import DomainError

ERROR_MESSAGES = {
    'task_description_missing_issue_reference': '説明には関連するIssue番号(例: #123)を含めてください。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
