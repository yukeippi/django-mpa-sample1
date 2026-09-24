from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from app.models.department import Department
from app.permissions import rule_sets


# ユーザーをグループ化し、権限を付与するためのモデル
class ManagementGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='管理グループ名')
    members = models.ManyToManyField(User, related_name='management_groups', blank=True, verbose_name='メンバー')
    is_admin = models.BooleanField(default=False, verbose_name='全社管理者')
    department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.CASCADE,
        related_name='management_groups', verbose_name='割当部門'
    )
    permission_set_id = models.IntegerField(null=True, blank=True, verbose_name='権限セット番号')

    class Meta:
        db_table = 'management_group'
        ordering = ['name']
        verbose_name = '管理グループ'
        verbose_name_plural = '管理グループ'
        # is_adminと部門・権限セット設定の整合性(全社管理者は部門・権限セットを持たず、それ以外は両方必須)。
        # 単一テーブル内の列同士の条件のためDB制約で表現できる。full_clean()もこれを検証するため、
        # 違反した条件ごとに文言を出せるよう制約を4つに分けている
        constraints = [
            models.CheckConstraint(
                condition=models.Q(is_admin=False) | models.Q(department__isnull=True),
                name='management_group_admin_without_department',
                violation_error_message='全社管理者グループには部門を設定できません。',
            ),
            models.CheckConstraint(
                condition=models.Q(is_admin=True) | models.Q(department__isnull=False),
                name='management_group_non_admin_requires_department',
                violation_error_message='全社管理者でない場合は部門の設定が必須です。',
            ),
            models.CheckConstraint(
                condition=models.Q(is_admin=False) | models.Q(permission_set_id__isnull=True),
                name='management_group_admin_without_permission_set',
                violation_error_message='全社管理者グループには権限セットを設定できません。',
            ),
            models.CheckConstraint(
                condition=models.Q(is_admin=True) | models.Q(permission_set_id__isnull=False),
                name='management_group_non_admin_requires_permission_set',
                violation_error_message='全社管理者でない場合は権限セットの設定が必須です。',
            ),
        ]

    def __str__(self):
        return self.name

    # 権限セット番号がレジストリに実在することを検証する(Pythonのレジストリを参照するためDB制約では表現できない)
    def clean(self):
        if self.permission_set_id is not None and self.permission_set_id not in rule_sets.REGISTRY:
            raise ValidationError('存在しない権限セット番号です。', code='management_group_unknown_permission_set')
