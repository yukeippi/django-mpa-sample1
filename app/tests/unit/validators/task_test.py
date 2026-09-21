import pytest
from django.core.exceptions import ValidationError
from app.validators.task import validate_description_contains_issue_reference


class TestValidateDescriptionContainsIssueReference:

    # 説明が空の場合は何も送出されないことを確認
    def test_blank_description_is_valid(self):
        validate_description_contains_issue_reference('')

    # 説明に#が含まれる場合は何も送出されないことを確認
    def test_description_with_hash_is_valid(self):
        validate_description_contains_issue_reference('関連Issue: #123')

    # 説明に#が含まれない場合はValidationErrorが送出されることを確認
    def test_description_without_hash_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            validate_description_contains_issue_reference('Issue番号を含まない説明文')
        assert exc_info.value.code == 'task_description_missing_issue_reference'
