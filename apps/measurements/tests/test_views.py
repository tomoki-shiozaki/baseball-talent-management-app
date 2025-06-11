from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date

from apps.measurements.models import Measurement

User = get_user_model()


class TestMeasurementCreateView(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player1", password="pass1234", role="player"
        )
        self.client.login(username="manager", password="pass1234")
        self.url = reverse("measurements:new", kwargs={"player_id": self.player.id})

    def test_get_request_returns_200_and_contains_player(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("player", response.context)
        self.assertEqual(response.context["player"], self.player)

    def test_post_creates_measurement_with_correct_fields(self):
        data = {
            "date": "2025-01-01",
            "sprint_50m": 6.2,
            "base_running": 13.1,
            "long_throw": 85,
            "straight_ball_speed": 125,
            "hit_ball_speed": 145,
            "swing_speed": 105,
            "bench_press": 95,
            "squat": 160,
        }
        response = self.client.post(self.url, data)
        # POST後はリダイレクト（成功）
        self.assertEqual(response.status_code, 302)

        # 作成されたMeasurementを取得
        measurement = Measurement.objects.latest("id")

        self.assertEqual(measurement.player, self.player)
        self.assertEqual(measurement.created_by, self.manager)
        self.assertEqual(measurement.status, "pending")
        self.assertEqual(str(measurement.date), data["date"])  # dateフィールドはdate型

    def test_invalid_player_id_returns_404(self):
        invalid_url = reverse("measurements:new", kwargs={"player_id": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
