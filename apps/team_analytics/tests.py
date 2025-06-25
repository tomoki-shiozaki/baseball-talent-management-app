from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from apps.measurements.models import Measurement

User = get_user_model()


# Create your tests here.
class TestPlayerDashboardView(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )

        # 8ヶ月分の測定データを作成
        for i in range(8):
            measurement_date = date.today().replace(day=1) - relativedelta(months=i)

            Measurement.objects.create(
                player=self.player,
                date=measurement_date,
                status="coach_approved",
                sprint_50m=6.0 + i * 0.1,  # 6.0, 6.1, ..., 6.7
                base_running=15.0,
                long_throw=60,
                straight_ball_speed=120,
                hit_ball_speed=130,
                swing_speed=100,
                bench_press=80,
                squat=100,
            )
        self.url = reverse("team_analytics:player_dashboard")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_access_denied_to_manager_coach_and_director(self):
        for user in [self.manager, self.coach, self.director]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)

    def test_access_permission(self):
        user = self.player
        self.client.login(username=user.username, password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_returns_recent_7_months(self):
        self.client.login(username="player", password="pass1234")

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("labels", response.context)
        self.assertIn("measurement_values", response.context)

        self.assertEqual(len(response.context["labels"]), 7)

        expected_keys = [
            "50m走",
            "ベースラン",
            "遠投",
            "ストレート球速",
            "打球速度",
            "スイング速度",
            "ベンチプレス",
            "スクワット",
        ]
        measurement_values = response.context["measurement_values"]
        self.assertEqual(set(measurement_values.keys()), set(expected_keys))
        self.assertIsInstance(measurement_values["50m走"], list)
        self.assertEqual(len(measurement_values["50m走"]), 7)

        sprint_values = measurement_values["50m走"]
        self.assertEqual(sprint_values[-1], 6.0)
        self.assertEqual(sprint_values[0], 6.6)


class TestDashboardView(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.url = reverse("team_analytics:staff_dashboard")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_access_denied_to_manager_and_player(self):
        for user in [
            self.manager,
            self.player,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_access_permission(self):
        for user in [
            self.coach,
            self.director,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    @patch("apps.team_analytics.views.Measurement.objects")
    def test_context_data(self, mock_measurement_objects):
        # TruncMonthで「2025-06-01」などのdatetimeオブジェクトを返す想定
        data = [
            {
                "month": datetime(2025, 6, 1),
                "sprint_50m": 7.0,
                "base_running": 10.0,
                "long_throw": None,
                "straight_ball_speed": 120.0,
                "hit_ball_speed": 80.0,
                "swing_speed": 50.0,
                "bench_press": 60.0,
                "squat": 100.0,
            },
            {
                "month": datetime(2025, 6, 1),
                "sprint_50m": 7.5,
                "base_running": 11.0,
                "long_throw": 30.0,
                "straight_ball_speed": 125.0,
                "hit_ball_speed": 85.0,
                "swing_speed": 55.0,
                "bench_press": 65.0,
                "squat": 110.0,
            },
        ]
        # values() の戻り値として iterable を返すモック
        mock_qs = data
        mock_measurement_objects.filter.return_value.annotate.return_value.values.return_value.order_by.return_value = (
            mock_qs
        )
        for user in [
            self.coach,
            self.director,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

            labels = response.context["labels"]
            measurement_values = response.context["measurement_values"]

            # ラベルが期待通りか（年月文字列）
            self.assertIn("2025-06", labels)

            # sprint_50m の平均が (7.0 + 7.5)/2 = 7.25 になっているか
            sprint_values = measurement_values["50m走"]
            self.assertAlmostEqual(sprint_values[0], 7.25)

            # long_throw は一つNone、もう一つ30なので平均は30
            long_throw_values = measurement_values["遠投"]
            self.assertAlmostEqual(long_throw_values[0], 30)

            self.client.logout()
