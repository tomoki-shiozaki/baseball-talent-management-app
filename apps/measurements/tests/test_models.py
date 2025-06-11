from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date

from apps.measurements.models import Measurement

User = get_user_model()


# Create your tests here.
class MeasurementModelTest(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.measurement = Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date(2025, 1, 1),
            sprint_50m=6.2,
            base_running=13.1,
            long_throw=85,
            straight_ball_speed=125,
            hit_ball_speed=145,
            swing_speed=105,
            bench_press=95,
            squat=160,
        )

    def test_create_measurement(self):
        self.assertEqual(self.measurement.player.username, "player")
        self.assertEqual(self.measurement.created_by.username, "manager")
        self.assertEqual(
            self.measurement.date,
            date(2025, 1, 1),
        )
        self.assertEqual(self.measurement.sprint_50m, 6.2)
        self.assertEqual(self.measurement.status, "pending")

    def test_str_method(self):
        expected_str = f"{self.player.username} - {self.measurement.date}"
        self.assertEqual(str(self.measurement), expected_str)
