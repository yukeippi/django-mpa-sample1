from typing import Self
from django.db import models
from app.models.company import Company


class DepartmentQuerySet(models.QuerySet):

    # 一覧表示で必要な関連(会社)をまとめて読み込む
    def with_company(self) -> Self:
        return self.select_related('company')

    # 同じ会社・同じ名前の部門に絞り込む(自分自身は除く)。Serviceの事前条件チェックから呼ぶ
    def duplicate_of(self, *, company, name, exclude_pk=None) -> Self:
        queryset = self.filter(company=company, name=name)
        if exclude_pk is not None:
            queryset = queryset.exclude(pk=exclude_pk)
        return queryset


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
            # 同じ会社内で部門名が重複しないようにする(競合時の最終防衛。Serviceの事前条件チェックが一次防衛)
            models.UniqueConstraint(fields=['company', 'name'], name='unique_department_name_per_company'),
        ]

    def __str__(self):
        return f'{self.company.name} / {self.name}'
