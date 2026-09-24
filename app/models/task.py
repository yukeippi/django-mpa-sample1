from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from app.validators import validate_description_contains_issue_reference


# タスク管理のためのサンプルモデル
class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=200, verbose_name='タイトル')
    description = models.TextField(
        blank=True, validators=[validate_description_contains_issue_reference], verbose_name='説明'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='todo',
        verbose_name='ステータス'
    )
    priority = models.IntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name='優先度'
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='担当者'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        verbose_name='作成者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    due_date = models.DateField(null=True, blank=True, verbose_name='期限')

    class Meta:
        db_table = 'task'
        ordering = ['-created_at']
        verbose_name = 'タスク'
        verbose_name_plural = 'タスク'
        constraints = [
            # 優先度は1〜5の範囲(DBでの保証。画面のエラーはpriorityフィールドのvalidatorsが出す)
            models.CheckConstraint(
                condition=models.Q(priority__gte=1) & models.Q(priority__lte=5), name='task_priority_range',
            ),
        ]

    def __str__(self):
        return self.title

    # 期限を過ぎているかチェック
    def is_overdue(self) -> bool:
        if not self.due_date:
            return False
        return self.due_date < timezone.now().date() and self.status != 'done'

    # 完了可能かチェック
    def can_be_completed(self) -> bool:
        return self.status in ['todo', 'in_progress']
