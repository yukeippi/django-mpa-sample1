from typing import Self
from django.db import models
from app.models.company import Company


class DepartmentQuerySet(models.QuerySet):

    # 一覧表示で必要な関連(会社)をまとめて読み込む
    def with_company(self) -> Self:
        return self.select_related('company')


# 部門情報のためのサンプルモデル
class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments', verbose_name='会社')
    name = models.CharField(max_length=100, verbose_name='部門名')

    objects = DepartmentQuerySet.as_manager()

    class Meta:
        db_table = 'department'
        ordering = ['company', 'name']
        verbose_name = '部門'
        verbose_name_plural = '部門'
        constraints = [
            # 同じ会社内で部門名が重複しないようにする(ModelFormがfull_clean()経由で画面のエラーにする)
            models.UniqueConstraint(fields=['company', 'name'], name='unique_department_name_per_company'),
        ]

    def __str__(self):
        return f'{self.company.name} / {self.name}'
