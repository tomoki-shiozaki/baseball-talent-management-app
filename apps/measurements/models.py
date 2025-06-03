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
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="measurements",
        verbose_name="選手",
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_measurements",
        verbose_name="作成者",
    )
    date = models.DateField(
        verbose_name="測定日",
        help_text="日付を YYYY-MM-DD の形式で入力してください。例: 2025-01-01",
    )

    sprint_50m = models.FloatField(
        verbose_name="50m走（秒）",
        help_text="50m走のタイム（秒）を入力してください",
    )
    base_running = models.FloatField(
        verbose_name="ベースランニング（秒）",
        help_text="ベースランニングのタイム（秒）を入力してください",
    )
    long_throw = models.IntegerField(
        verbose_name="遠投（m）",
        help_text="遠投距離（メートル）を入力してください",
    )
    straight_ball_speed = models.IntegerField(
        verbose_name="ストレート球速（km/h）",
        help_text="ストレートの球速（km/h）を入力してください",
    )
    hit_ball_speed = models.IntegerField(
        verbose_name="打球速度（km/h）",
        help_text="打球速度（km/h）を入力してください",
    )
    swing_speed = models.IntegerField(
        verbose_name="スイング速度（km/h）",
        help_text="スイング速度（km/h）を入力してください",
    )
    bench_press = models.IntegerField(
        verbose_name="ベンチプレス（kg）",
        help_text="ベンチプレスの重量（kg）を入力してください",
    )
    squat = models.IntegerField(
        verbose_name="スクワット（kg）",
        help_text="スクワットの重量（kg）を入力してください",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="ステータス",
    )

    def __str__(self):
        return f"{self.player.username} - {self.date}"

    class Meta:
        verbose_name = "測定記録"
        verbose_name_plural = "測定記録"


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
