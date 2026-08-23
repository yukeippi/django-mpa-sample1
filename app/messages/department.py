from app.errors.base import DomainError

ERROR_MESSAGES = {
    'duplicate_department_name': 'この会社には同じ名前の部門が既に存在します。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
