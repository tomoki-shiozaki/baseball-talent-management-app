from django.db import models
from django.contrib.auth import get_user_model

from apps.measurements.models import Measurement


# Create your models here.
class MeasurementApproval(models.Model):
    STEP_CHOICES = [
        ("self", "部員による承認"),
        ("coach", "コーチの最終承認"),
    ]
    STATUS_CHOICES = [
        ("approved", "承認"),
        ("rejected", "否認"),
    ]

    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, related_name="approvals"
    )
    approver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=get_user_model().ROLE_CHOICES)
    step = models.CharField(max_length=10, choices=STEP_CHOICES)
    approved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.measurement} by {self.approver.username} ({self.get_step_display()})"

    class Meta:
        verbose_name = "承認履歴"
        verbose_name_plural = "承認履歴"
        unique_together = ("measurement", "approver", "step")
