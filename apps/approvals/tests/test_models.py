from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.measurements.models import Measurement
from apps.approvals.models import MeasurementApproval

User = get_user_model()


class TestMeasurementApprovalModel(TestCase):
    def setUp(self):
        # ユーザーを作成
        self.manager = User.objects.create_user(
            username="manager1", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player1", password="pass1234", role="player"
        )
        self.coach = User.objects.create_user(
            username="coach1", password="pass1234", role="coach"
        )

        # 測定記録を作成
        self.measurement = Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=timezone.now().date(),
            sprint_50m=6.5,
            base_running=12.0,
            long_throw=80,
            straight_ball_speed=120,
            hit_ball_speed=140,
            swing_speed=100,
            bench_press=90,
            squat=150,
            status="pending",
        )

    def test_create_measurement_approval(self):
        approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="approved",
            comment="問題ありません",
        )

        self.assertEqual(approval.measurement, self.measurement)
        self.assertEqual(approval.approver, self.player)
        self.assertEqual(approval.role, "player")
        self.assertEqual(approval.step, "self")
        self.assertEqual(approval.status, "approved")
        self.assertEqual(approval.comment, "問題ありません")
        self.assertIsNotNone(approval.created_at)
        self.assertIn("player1", str(approval))  # __str__ のテスト

    def test_unique_constraint(self):
        # まず1つ目を作成
        MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="approved",
        )
        # 同じmeasurement, approver, stepで2つ目作成するとエラーになるはず
        with self.assertRaises(Exception):
            MeasurementApproval.objects.create(
                measurement=self.measurement,
                approver=self.player,
                role="player",
                step="self",
                status="rejected",
            )

    def test_str_method(self):
        approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.coach,
            role="coach",
            step="coach",
            status="rejected",
            comment="問題があります",
        )
        expected_str = f"{self.measurement} by {self.coach.username} (コーチの最終承認)"
        self.assertEqual(str(approval), expected_str)
