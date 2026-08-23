from app.errors.base import DomainError

ERROR_MESSAGES = {
    'parent_department_company_mismatch': '親部門は同じ会社に属している必要があります。',
    'self_parent_department': '親部門に自分自身を指定することはできません。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
