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
            models.UniqueConstraint(fields=['employee', 'department'], name='unique_employee_department'),
        ]

    def __str__(self):
        return f'{self.employee} - {self.department}'
