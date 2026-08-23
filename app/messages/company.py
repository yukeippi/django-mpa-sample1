from app.errors.base import DomainError

ERROR_MESSAGES = {
    'duplicate_company_name': 'この会社名は既に使用されています。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
