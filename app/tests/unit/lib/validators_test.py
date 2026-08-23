import pytest
from django.core.exceptions import ValidationError
from app.lib.validators import ContainsCharacterValidator

# NOTE: ContainsCharacterValidatorはTask.descriptionの検証には使われなくなった
# (app/validators/task.pyのPure Functionに置き換え。Validator Rules参照)。
# このクラス自体は過去のマイグレーション(0002_alter_task_description)がシリアライズ済みの
# 参照を持つため、マイグレーション履歴との整合性を保つ目的でのみ残している


# ContainsCharacterValidator単体のテストクラス
class TestContainsCharacterValidator:

    # 指定した文字が含まれていれば例外が発生しないことを確認
    def test_valid_when_character_present(self):
        validator = ContainsCharacterValidator('@')
        validator('user@example.com')

    # 指定した文字が含まれていなければValidationErrorが発生することを確認
    def test_invalid_when_character_missing(self):
        validator = ContainsCharacterValidator('@')
        with pytest.raises(ValidationError):
            validator('user-example.com')

    # messageを指定した場合、そのメッセージがエラーに使われることを確認
    def test_custom_message_is_used(self):
        validator = ContainsCharacterValidator('@', message='カスタムメッセージ')
        with pytest.raises(ValidationError, match='カスタムメッセージ'):
            validator('invalid')
