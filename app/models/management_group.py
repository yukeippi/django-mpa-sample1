from django.db import models
from django.contrib.auth.models import User
from app.models.department import Department


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
        constraints = [
            # is_adminと部門・権限セット設定の整合性(全社管理者は部門・権限セットを持たず、それ以外は両方必須)。
            # 単一テーブル内の列同士の条件のためDB制約で表現できる。権限セット番号が実在するかはPythonの
            # レジストリ(rule_sets.REGISTRY)を参照する必要があり、DBでは保証できないためServiceの事前条件チェックのみで守る
            models.CheckConstraint(
                condition=(
                    models.Q(is_admin=True, department__isnull=True, permission_set_id__isnull=True)
                    | models.Q(is_admin=False, department__isnull=False, permission_set_id__isnull=False)
                ),
                name='management_group_admin_consistency',
            ),
        ]

    def __str__(self):
        return self.name
