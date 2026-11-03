from typing import Self
from django.db import models
from app.models.employee import Employee
from app.models.department import Department


class EmployeeDepartmentQuerySet(models.QuerySet):

    # 主務の所属に絞り込む
    def primary(self) -> Self:
        return self.filter(is_primary=True)


# 社員と部門の所属関係(主務/兼務)を表す中間モデル
class EmployeeDepartment(models.Model):
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, related_name='employee_departments', verbose_name='社員'
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='employee_departments', verbose_name='部門'
    )
    is_primary = models.BooleanField(default=False, verbose_name='主務')

    objects = EmployeeDepartmentQuerySet.as_manager()

    class Meta:
        db_table = 'employee_department'
        verbose_name = '社員所属部門'
        verbose_name_plural = '社員所属部門'
        constraints = [
            # 同じ社員・部門の組み合わせが重複しないようにする(full_clean()もこれを検証する)
            models.UniqueConstraint(
                fields=['employee', 'department'], name='unique_employee_department',
                violation_error_message='この社員は既にこの部門に所属しています。',
            ),
            # 主務は1人1つまで(主務の行だけを対象にした条件付きの一意制約。兼務はいくつでも持てる)
            models.UniqueConstraint(
                fields=['employee'], condition=models.Q(is_primary=True), name='unique_primary_department_per_employee',
                violation_error_message='この社員には既に主務の部門があります。',
            ),
        ]

    def __str__(self):
        return f'{self.employee} - {self.department}'
