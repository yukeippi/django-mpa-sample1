from django.db import models
from app.models.department import Department


# 権限判定用の部門階層(親部門)を表すモデル。全ての部門がレコードを持つ必要はない
class DepartmentHierarchy(models.Model):
    department = models.OneToOneField(
        Department, on_delete=models.CASCADE, related_name='hierarchy', verbose_name='部門'
    )
    parent_department = models.ForeignKey(
        Department, null=True, blank=True, on_delete=models.CASCADE,
        related_name='child_hierarchies', verbose_name='親部門'
    )

    class Meta:
        db_table = 'department_hierarchy'
        verbose_name = '部門階層'
        verbose_name_plural = '部門階層'
        constraints = [
            # 親部門に自分自身を指定できないようにする(同一テーブル内の比較のためDB制約で表現できる)
            models.CheckConstraint(
                condition=~models.Q(parent_department=models.F('department')),
                name='department_hierarchy_parent_not_self',
            ),
        ]

    def __str__(self):
        return f'{self.department} (親: {self.parent_department})'
