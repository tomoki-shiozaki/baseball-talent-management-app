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


class TestPlayerComparisonView(TestCase):

    def setUp(self):
        # ユーザー作成
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.other_player = User.objects.create_user(
            username="other_player", password="pass1234", role="player"
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

        self.url = reverse("team_analytics:player_comparison")

        Measurement.objects.create(
            player=self.player,
            sprint_50m=7.0,
            base_running=15.0,
            long_throw=80,
            straight_ball_speed=130,
            hit_ball_speed=100,
            swing_speed=90,
            bench_press=70,
            squat=90,
            status="coach_approved",
            date=datetime(2025, 6, 1),
        )
        Measurement.objects.create(
            player=self.other_player,
            sprint_50m=7.5,
            base_running=14.5,
            long_throw=85,
            straight_ball_speed=135,
            hit_ball_speed=105,
            swing_speed=95,
            bench_press=75,
            squat=95,
            status="coach_approved",
            date=datetime(2025, 6, 1),
        )
        Measurement.objects.create(
            player=self.player,
            sprint_50m=6.4,
            base_running=15.2,
            long_throw=82,
            straight_ball_speed=132,
            hit_ball_speed=102,
            swing_speed=92,
            bench_press=72,
            squat=92,
            status="coach_approved",
            date=datetime(2025, 4, 1),
        )

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

    def test_view_context_data_for_player(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("player", response.context)
        self.assertEqual(response.context["player"], self.player)

        # labels のフォーマット確認
        labels = response.context.get("labels", [])
        self.assertTrue(all(isinstance(label, str) for label in labels))
        for label in labels:
            self.assertRegex(label, r"^\d{4}-\d{2}$")

        # team_values と player_values のキー確認
        measurement_fields = {
            "50m走",
            "ベースラン",
            "遠投",
            "ストレート球速",
            "打球速度",
            "スイング速度",
            "ベンチプレス",
            "スクワット",
        }
        self.assertEqual(
            set(response.context["team_values"].keys()), measurement_fields
        )
        self.assertEqual(
            set(response.context["player_values"].keys()), measurement_fields
        )

        # いずれかの値が None ではないこと確認
        some_label = next(iter(measurement_fields))
        team_vals = response.context["team_values"][some_label]
        player_vals = response.context["player_values"][some_label]
        self.assertTrue(any(v is not None for v in team_vals))
        self.assertTrue(any(v is not None for v in player_vals))

        # チームの平均値のテスト
        team_values = response.context["team_values"]
        self.assertIsInstance(team_values["50m走"], list)
        self.assertEqual(len(team_values["50m走"]), 2)

        team_sprint_values = team_values["50m走"]
        # sprint_50m の2025-06の平均値が (7.0 + 7.5)/2 = 7.25 になっているか
        self.assertEqual(team_sprint_values[1], 7.25)
        # sprint_50m の2025-04の平均値が 6.4 になっているか
        self.assertEqual(team_sprint_values[0], 6.4)

        # 部員の測定値のテスト
        player_values = response.context["player_values"]
        self.assertIsInstance(player_values["50m走"], list)
        self.assertEqual(len(player_values["50m走"]), 2)

        player_sprint_values = player_values["50m走"]
        # sprint_50m の2025-06のplayerの測定値が 7.0 になっているか
        self.assertEqual(player_sprint_values[1], 7.0)
        # sprint_50m の2025-04のplayerの測定値が 6.4 になっているか
        self.assertEqual(player_sprint_values[0], 6.4)


class TestStaffDashboardView(TestCase):
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


class TestStaffComparisonEntryView(TestCase):
    def setUp(self):
        # ロールごとのユーザーを作成
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )

        # 選手データ（並び替え検証用）
        self.p1 = User.objects.create_user(
            username="p1",
            password="pass1234",
            role="player",
            grade=2,
            last_name="Tanaka",
            first_name="Ichiro",
        )
        self.p2 = User.objects.create_user(
            username="p2",
            password="pass1234",
            role="player",
            grade=1,
            last_name="Abe",
            first_name="Kenta",
        )
        self.p3 = User.objects.create_user(
            username="p3",
            password="pass1234",
            role="player",
            grade=2,
            last_name="Tanaka",
            first_name="Jiro",
        )
        self.inactive_player = User.objects.create_user(
            username="inactive",
            password="pass1234",
            role="player",
            grade=3,
            last_name="Inactive",
            first_name="User",
            is_active=False,
        )

        self.url = reverse("team_analytics:staff_comparison_entry")

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_access_denied_for_non_staff_roles(self):
        for user in [self.player, self.manager]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)

    def test_access_allowed_for_coach_and_director(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(
                response, "team_analytics/staff_comparison_entry.html"
            )

    def test_context_contains_ordered_active_players(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)

            players = response.context["players"]
            self.assertEqual(len(players), 4)  # 非アクティブは含まれない

            # 並び順: grade 昇順 → last_name → first_name。Noneが最初にくる
            expected_order = [self.player, self.p2, self.p1, self.p3]
            self.assertEqual(list(players), expected_order)


class TestStaffPlayerComparisonView(TestCase):

    def setUp(self):
        # ユーザー作成
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.other_player = User.objects.create_user(
            username="other_player", password="pass1234", role="player"
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

        self.url = reverse("team_analytics:staff_player_comparison")

        # 測定データ作成
        Measurement.objects.create(
            player=self.player,
            sprint_50m=7.0,
            base_running=15.0,
            long_throw=80,
            straight_ball_speed=130,
            hit_ball_speed=100,
            swing_speed=90,
            bench_press=70,
            squat=90,
            status="coach_approved",
            date=datetime(2025, 6, 1),
        )
        Measurement.objects.create(
            player=self.other_player,
            sprint_50m=7.5,
            base_running=14.5,
            long_throw=85,
            straight_ball_speed=135,
            hit_ball_speed=105,
            swing_speed=95,
            bench_press=75,
            squat=95,
            status="coach_approved",
            date=datetime(2025, 6, 1),
        )
        Measurement.objects.create(
            player=self.player,
            sprint_50m=6.4,
            base_running=15.2,
            long_throw=82,
            straight_ball_speed=132,
            hit_ball_speed=102,
            swing_speed=92,
            bench_press=72,
            squat=92,
            status="coach_approved",
            date=datetime(2025, 4, 1),
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_access_denied_to_non_coach_director(self):
        for user in [self.manager, self.player]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)

    def test_access_allowed_to_coach_and_director(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass1234")
            # player_idパラメータ必須なのでつける
            response = self.client.get(self.url, {"player_id": self.player.id})
            self.assertEqual(response.status_code, 200)

    def test_404_if_invalid_player_id(self):
        self.client.login(username=self.coach.username, password="pass1234")
        response = self.client.get(self.url, {"player_id": 99999})
        self.assertEqual(response.status_code, 404)

    def test_context_data_contents(self):
        self.client.login(username=self.coach.username, password="pass1234")
        response = self.client.get(self.url, {"player_id": self.player.id})
        self.assertEqual(response.status_code, 200)

        context = response.context
        # playerが正しいか
        self.assertEqual(context["player"], self.player)

        # player_listにplayerとother_playerが含まれているか
        player_usernames = [p.username for p in context["player_list"]]
        self.assertIn(self.player.username, player_usernames)
        self.assertIn(self.other_player.username, player_usernames)

        # labelsが存在し年月フォーマットか
        labels = context.get("labels", [])
        self.assertTrue(all(isinstance(label, str) for label in labels))
        for label in labels:
            self.assertRegex(label, r"^\d{4}-\d{2}$")

        # team_values, player_valuesにキーがあるか
        expected_labels = {
            "50m走",
            "ベースラン",
            "遠投",
            "ストレート球速",
            "打球速度",
            "スイング速度",
            "ベンチプレス",
            "スクワット",
        }
        self.assertEqual(set(context["team_values"].keys()), expected_labels)
        self.assertEqual(set(context["player_values"].keys()), expected_labels)

        # いずれかの値がNoneでないこと確認
        some_label = next(iter(expected_labels))
        self.assertTrue(any(v is not None for v in context["team_values"][some_label]))
        self.assertTrue(
            any(v is not None for v in context["player_values"][some_label])
        )

        # sprint_50m の2025-06の平均が (7.0 + 7.5) / 2 = 7.25 か確認
        # context["labels"] のどのインデックスに '2025-06' があるか調べる
        idx = None
        for i, label in enumerate(labels):
            if label == "2025-06":
                idx = i
                break
        self.assertIsNotNone(idx)
        self.assertEqual(idx, 1)

        self.assertAlmostEqual(context["team_values"]["50m走"][idx], 7.25)
        self.assertEqual(context["player_values"]["50m走"][idx], 7.0)
