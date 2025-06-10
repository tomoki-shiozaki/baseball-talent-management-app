from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import date

from apps.measurements.models import Measurement
from apps.approvals.models import MeasurementApproval

User = get_user_model()


class TestHomePage(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )

    def test_view_url_by_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_manager_rejected_count(self):
        Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date.today(),
            sprint_50m=6.2,
            base_running=13.1,
            long_throw=85,
            straight_ball_speed=125,
            hit_ball_speed=145,
            swing_speed=105,
            bench_press=95,
            squat=160,
            status="rejected",
        )
        self.client.login(username="manager", password="pass1234")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["rejected_count"], 1)

    def test_player_pending_count(self):
        Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date.today(),
            sprint_50m=6.2,
            base_running=13.1,
            long_throw=85,
            straight_ball_speed=125,
            hit_ball_speed=145,
            swing_speed=105,
            bench_press=95,
            squat=160,
            status="pending",
        )
        self.client.login(username="player", password="pass1234")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["pending_count"], 1)

    def test_coach_pending_count(self):
        m = Measurement.objects.create(
            player=self.player,
            created_by=self.manager,
            date=date.today(),
            sprint_50m=6.2,
            base_running=13.1,
            long_throw=85,
            straight_ball_speed=125,
            hit_ball_speed=145,
            swing_speed=105,
            bench_press=95,
            squat=160,
            status="player_approved",
        )
        MeasurementApproval.objects.create(
            measurement=m,
            approver=self.player,
            role="player",
            step="self",
            status="approved",
        )
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["coach_pending_count"], 1)
