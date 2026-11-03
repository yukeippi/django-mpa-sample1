from django.core.exceptions import ValidationError
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

    objects = models.Manager()

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

    # 親部門は同じ会社の部門でなければならない(モデルをまたぐ整合性はDB制約で表現できないため、clean()で検証する)
    def clean(self):
        if self.department_id is None or self.parent_department_id is None:
            return
        if self.parent_department.company_id != self.department.company_id:
            raise ValidationError({'parent_department': ValidationError(
                '親部門には同じ会社の部門を指定してください。', code='department_hierarchy_parent_company_mismatch'
            )})
