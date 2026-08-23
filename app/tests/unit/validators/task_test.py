import pytest
from app.errors.task import TaskDescriptionMissingIssueReferenceError
from app.validators.task import validate_description_contains_issue_reference


class TestValidateDescriptionContainsIssueReference:

    # 説明が空の場合は検証されずそのまま返ることを確認
    def test_blank_description_is_valid(self):
        assert validate_description_contains_issue_reference('') == ''

    # 説明に#が含まれる場合はそのまま返ることを確認
    def test_description_with_hash_is_valid(self):
        value = '関連Issue: #123'
        assert validate_description_contains_issue_reference(value) == value

    # 説明に#が含まれない場合はTaskDescriptionMissingIssueReferenceErrorが送出されることを確認
    def test_description_without_hash_raises_error(self):
        with pytest.raises(TaskDescriptionMissingIssueReferenceError):
            validate_description_contains_issue_reference('Issue番号を含まない説明文')
