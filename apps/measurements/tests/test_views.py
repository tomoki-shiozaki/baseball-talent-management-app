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
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.url = reverse("measurements:new", kwargs={"player_id": self.player.id})

    def test_access_granted_to_manager(self):
        self.client.login(username="manager", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("player", response.context)
        self.assertEqual(response.context["player"], self.player)
        self.client.logout()

    def test_access_denied_to_player_and_coach_and_director(self):
        for user in [
            self.player,
            self.coach,
            self.director,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_get_request_returns_200_and_contains_player(self):
        self.client.login(username="manager", password="pass1234")
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
        self.client.login(username="manager", password="pass1234")
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


class TestPlayerListView(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player1", password="pass1234", role="player"
        )
        self.url = reverse("measurements:player_list")

    def test_get_request_returns_200_and_contains_player(self):
        self.client.login(username="manager", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        players = response.context["players"]
        self.assertIn(self.player, players)
        self.assertNotIn(self.manager, players)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class TestMyMeasurementListView(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player1",
            password="pass1234",
            role="player",
            first_name="太郎",
            last_name="山田",
        )
        self.other_player = User.objects.create_user(
            username="player2", password="pass1234", role="player"
        )

        # 自分の承認済み記録（表示対象）
        self.my_record = Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date(2025, 6, 1),
            status="coach_approved",
            sprint_50m=6.0,
            base_running=13.0,
            long_throw=85,
            straight_ball_speed=130,
            hit_ball_speed=125,
            swing_speed=110,
            bench_press=90,
            squat=140,
        )

        # 他人の記録（表示対象外）
        Measurement.objects.create(
            player=self.other_player,
            created_by=self.manager,
            date=date(2025, 6, 1),
            status="coach_approved",
            sprint_50m=6.0,
            base_running=13.0,
            long_throw=85,
            straight_ball_speed=130,
            hit_ball_speed=125,
            swing_speed=110,
            bench_press=90,
            squat=140,
        )

        self.client.login(username="player1", password="pass1234")
        self.url = reverse("measurements:my_records")

    def test_only_approved_measurements_for_logged_in_user_are_displayed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context["measurements"]
        self.assertIn(self.my_record, measurements)
        self.assertEqual(len(measurements), 1)  # 他人の記録は含まれない

    def test_context_contains_player_name_and_filters(self):
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["player_name"], "太郎 山田")
        self.assertEqual(context["current_order"], "desc")
        self.assertEqual(context["current_status"], "approved")


class TestMemberListView(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach", password="pass", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass", role="director"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass", role="player"
        )

        self.active_player = User.objects.create_user(
            username="active_player", password="pass", role="player", status="active"
        )
        self.inactive_player = User.objects.create_user(
            username="inactive_player",
            password="pass",
            role="player",
            status="inactive",
        )

        self.url = reverse("measurements:member_list")

    def test_access_granted_to_coach_and_director(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_access_denied_to_manager_and_player(self):
        for user in [self.manager, self.player]:
            self.client.login(username=user.username, password="pass")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_queryset_only_returns_active_players(self):
        self.client.login(username="coach", password="pass")
        response = self.client.get(self.url)
        players = response.context["players"]
        self.assertIn(self.active_player, players)
        self.assertNotIn(self.inactive_player, players)


class TestPlayerMeasurementListView(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach", password="pass", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass", role="director"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass", role="manager"
        )
        self.player = User.objects.create_user(
            username="player1",
            password="pass",
            role="player",
            first_name="太郎",
            last_name="山田",
        )
        self.other_player = User.objects.create_user(
            username="player2", password="pass1234", role="player"
        )
        self.player_record = Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date(2025, 6, 1),
            status="coach_approved",
            sprint_50m=6.0,
            base_running=13.0,
            long_throw=85,
            straight_ball_speed=130,
            hit_ball_speed=125,
            swing_speed=110,
            bench_press=90,
            squat=140,
        )

        Measurement.objects.create(
            player=self.other_player,
            created_by=self.manager,
            date=date(2025, 6, 1),
            status="coach_approved",
            sprint_50m=6.0,
            base_running=13.0,
            long_throw=85,
            straight_ball_speed=130,
            hit_ball_speed=125,
            swing_speed=110,
            bench_press=90,
            squat=140,
        )

        self.url = reverse(
            "measurements:player_measurement_list", kwargs={"player_id": self.player.id}
        )

    def test_access_granted_to_coach_and_director(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_access_denied_to_manager_and_player(self):
        for user in [self.manager, self.player]:
            self.client.login(username=user.username, password="pass")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_only_approved_measurements_for_player_are_displayed(self):
        self.client.login(username="coach", password="pass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context["measurements"]
        self.assertIn(self.player_record, measurements)
        self.assertEqual(len(measurements), 1)  # 他人の記録は含まれない

    def test_context_contains_player_name_and_filters(self):
        self.client.login(username="coach", password="pass")
        response = self.client.get(self.url)
        context = response.context
        self.assertEqual(context["player_name"], "太郎 山田")
        self.assertEqual(context["current_order"], "desc")
        self.assertEqual(context["current_status"], "approved")
