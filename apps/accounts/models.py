from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ("manager", "マネージャー"),
        ("player", "部員"),
        ("coach", "コーチ"),
        ("director", "監督"),
    ]
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name="ロール",
        help_text="ユーザーの役割を選択してください。",
    )
    status = models.CharField(
        max_length=10,
        choices=[("active", "在籍中"), ("retired", "退部")],
        default="active",
    )
    grade = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="学年",
        help_text="部員の学年を入力してください（例：1〜3）",
    )

    @property
    def is_manager(self):
        return self.role == "manager"

    @property
    def is_player(self):
        return self.role == "player"

    @property
    def is_coach(self):
        return self.role == "coach"

    @property
    def is_director(self):
        return self.role == "director"
