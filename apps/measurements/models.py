from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
from django.db import models
from django.contrib.auth import get_user_model


class Measurement(models.Model):
    STATUS_CHOICES = [
        ("draft", "下書き"),
        ("pending", "承認待ち"),
        ("player_approved", "部員承認済み"),
        ("coach_approved", "コーチ承認済み"),
    ]

    player = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="measurements"
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_measurements",
    )
    date = models.DateField()

    # 測定項目
    sprint_50m = models.FloatField(help_text="50m走（秒）")
    base_running = models.FloatField(help_text="ベースランニング（秒）")
    long_throw = models.IntegerField(help_text="遠投（m）")
    straight_ball_speed = models.IntegerField(help_text="ストレート球速（km/h）")
    hit_ball_speed = models.IntegerField(help_text="打球速度（km/h）")
    swing_speed = models.IntegerField(help_text="スイング速度（km/h）")
    bench_press = models.IntegerField(help_text="ベンチプレス（kg）")
    squat = models.IntegerField(help_text="スクワット（kg）")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    def __str__(self):
        return f"{self.player.username} - {self.date}"

    class Meta:
        verbose_name = "測定記録"
        verbose_name_plural = "測定記録"


class MeasurementApproval(models.Model):
    measurement = models.ForeignKey(
        Measurement, on_delete=models.CASCADE, related_name="approvals"
    )
    approver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=get_user_model().ROLE_CHOICES)
    approved_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, choices=[("approved", "承認"), ("rejected", "否認")]
    )

    def __str__(self):
        return f"{self.measurement} by {self.approver.username}"

    class Meta:
        verbose_name = "承認履歴"
        verbose_name_plural = "承認履歴"
