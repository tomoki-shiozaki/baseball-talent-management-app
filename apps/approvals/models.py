from django.db import models
from django.contrib.auth import get_user_model

from apps.measurements.models import Measurement


# Create your models here.
class MeasurementApproval(models.Model):
    # 誰が承認するか。部員またはコーチ。
    STEP_CHOICES = [
        ("self", "部員による承認"),
        ("coach", "コーチの最終承認"),
    ]
    STATUS_CHOICES = [
        ("approved", "承認"),
        ("rejected", "否認"),
    ]

    measurement = models.ForeignKey(
        Measurement,
        on_delete=models.CASCADE,
        related_name="approvals",
        verbose_name="測定記録",
    )
    # 誰がその承認をしたか
    approver = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="承認者",
    )
    # 承認した人のロール
    role = models.CharField(
        max_length=10,
        choices=get_user_model().ROLE_CHOICES,
        verbose_name="承認者の立場",
    )
    step = models.CharField(
        max_length=10,
        choices=STEP_CHOICES,
        verbose_name="承認ステップ",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="承認日時",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        verbose_name="承認ステータス",
    )
    comment = models.TextField(
        blank=True,
        verbose_name="コメント",
    )

    def __str__(self):
        return f"{self.measurement} by {self.approver.username} ({self.get_step_display()})"

    class Meta:
        verbose_name = "承認履歴"
        verbose_name_plural = "承認履歴"
        constraints = [
            models.UniqueConstraint(
                fields=["measurement", "approver", "step"],
                name="unique_approval_once",
            )
        ]
