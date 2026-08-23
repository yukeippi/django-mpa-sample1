from app.errors.base import DomainError

ERROR_MESSAGES = {
    'duplicate_employee_department': 'この社員は既にこの部門に所属しています。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
