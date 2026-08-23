from app.errors.base import DomainError

ERROR_MESSAGES = {
    'duplicate_management_group_name': 'この管理グループ名は既に使用されています。',
    'admin_group_cannot_have_department': '全社管理者グループには部門を設定できません。',
    'non_admin_group_requires_department': '全社管理者でない場合は部門の設定が必須です。',
    'admin_group_cannot_have_permission_set': '全社管理者グループには権限セットを設定できません。',
    'non_admin_group_requires_permission_set': '全社管理者でない場合は権限セットの設定が必須です。',
    'invalid_permission_set_id': '存在しない権限セット番号です。',
}


# DomainErrorを日本語メッセージに変換する
def message_for_error(error: DomainError) -> str:
    return ERROR_MESSAGES.get(error.code, '処理を完了できませんでした。')
