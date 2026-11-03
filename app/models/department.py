from typing import Self
from django.core.exceptions import ValidationError
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
        verbose_name = '部門'
        verbose_name_plural = '部門'
        constraints = [
            # 同じ会社内で部門名が重複しないようにする(ModelFormがfull_clean()経由で画面のエラーにする)
            models.UniqueConstraint(fields=['company', 'name'], name='unique_department_name_per_company'),
        ]

    def __str__(self):
        return f'{self.company.name} / {self.name}'

    # 親部門・子部門がある部門は会社を変更できない(親子関係が会社をまたぐ状態を防ぐ。保存済みの会社と比べるため、clean()で検証する)
    def clean(self):
        if self.pk is None or self.company_id is None:
            return
        saved_company_id = Department.objects.filter(pk=self.pk).values_list('company_id', flat=True).first()
        if saved_company_id is None or saved_company_id == self.company_id:
            return
        has_parent = Department.objects.filter(pk=self.pk, hierarchy__parent_department__isnull=False).exists()
        if has_parent or self.child_hierarchies.exists():
            raise ValidationError({'company': ValidationError(
                '親部門・子部門がある部門は会社を変更できません。先に親子関係を外してください。',
                code='department_company_change_with_hierarchy',
            )})
