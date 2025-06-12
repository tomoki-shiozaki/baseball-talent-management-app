from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.measurements.models import Measurement
from apps.approvals.models import MeasurementApproval
from datetime import date
from django.utils import timezone

User = get_user_model()


class TestRejectedApprovalListView(TestCase):
    def setUp(self):
        # マネージャーと部員のユーザー作成
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )

        # 測定記録（否認、未再作成）
        self.measurement = Measurement.objects.create(
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

        self.approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="rejected",
            comment="データ不備",
        )

    def test_access_denied_for_non_manager(self):
        self.client.login(username="player", password="pass1234")
        url = reverse("approvals:manager_rejected_approval_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_manager_can_see_rejected_approvals(self):
        self.client.login(username="manager", password="pass1234")
        url = reverse("approvals:manager_rejected_approval_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        approvals = response.context["approvals"]
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0], self.approval)

    def test_anonymous_user_redirected_to_login(self):
        url = reverse("approvals:manager_rejected_approval_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_recreated_measurement_not_included(self):
        self.measurement.recreated_at = timezone.now()
        self.measurement.save()

        self.client.login(username="manager", password="pass1234")
        url = reverse("approvals:manager_rejected_approval_list")
        response = self.client.get(url)
        approvals = response.context["approvals"]
        self.assertEqual(len(approvals), 0)  # 再作成済みなので出ない


class TestRejectedApprovalDetailView(TestCase):
    def setUp(self):
        # マネージャーと部員のユーザー作成
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )

        # 測定記録（否認、未再作成）
        self.measurement = Measurement.objects.create(
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

        self.approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="rejected",
            comment="データ不備",
        )

    def test_manager_can_access(self):
        self.client.login(username="manager", password="pass1234")
        url = reverse(
            "approvals:manager_rejected_approval_detail", args=[self.approval.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_manager_cannot_access(self):
        self.client.login(username="player", password="pass1234")
        url = reverse(
            "approvals:manager_rejected_approval_detail", args=[self.approval.pk]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access(self):
        url = reverse(
            "approvals:manager_rejected_approval_detail", args=[self.approval.pk]
        )
        response = self.client.get(url)
        # ログインしていないのでログインページにリダイレクトされる
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)


class TestMeasurementRecreateView(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            username="manager", password="pass", role="manager"
        )
        self.player = User.objects.create_user(
            username="player", password="pass", role="player"
        )

        self.original = Measurement.objects.create(
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

        self.approval = MeasurementApproval.objects.create(
            measurement=self.original,
            approver=self.player,
            role="player",
            step="self",
            status="rejected",
        )

        self.url = reverse(
            "approvals:manager_rejected_measurement_recreate", args=[self.approval.pk]
        )

    def test_only_manager_can_access(self):
        self.client.login(username="player", password="pass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_initial_values_are_copied_from_original(self):
        self.client.login(username="manager", password="pass")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "145")  # hit_ball_speed の値

    def test_submission_creates_new_measurement_and_marks_original(self):
        self.client.login(username="manager", password="pass")
        response = self.client.post(
            self.url,
            {
                "date": date.today(),
                "sprint_50m": 6.0,
                "base_running": 13.0,
                "long_throw": 86,
                "straight_ball_speed": 126,
                "hit_ball_speed": 146,
                "swing_speed": 106,
                "bench_press": 96,
                "squat": 161,
            },
        )
        self.assertRedirects(response, reverse("home"))

        # 新しい記録ができているか
        recreated = Measurement.objects.latest("id")
        self.assertEqual(recreated.player, self.player)
        self.assertEqual(recreated.created_by, self.manager)
        self.assertEqual(recreated.status, "pending")

        # 古いレコードに再作成日時が記録されたか
        self.original.refresh_from_db()
        self.assertIsNotNone(self.original.recreated_at)


class TestPlayerPendingApprovalListView(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )

        self.measurement = Measurement.objects.create(
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

        self.url = reverse("approvals:player_pending_approvals")

    def test_player_can_access_and_see_measurements(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context["measurements"]
        self.assertIn(self.measurement, measurements)

    def test_manager_cannot_access(self):
        self.client.login(username="manager", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_only_unapproved_measurements_shown(self):
        self.client.login(username="player", password="pass1234")

        # 承認済みの承認履歴を作る
        self.approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="approved",
        )

        response = self.client.get(self.url)
        measurements = response.context["measurements"]

        # もう承認済みだから一覧に表示されない
        self.assertNotIn(self.measurement, measurements)


class TestPlayerApprovalCreateView(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.other_player = User.objects.create_user(
            username="other_player", password="pass1234", role="player"
        )

        self.measurement = Measurement.objects.create(
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

        self.url = reverse(
            "approvals:player_approve",
            kwargs={"measurement_id": self.measurement.id},
        )

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_uses_correct_template(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "approvals/player_approval_form.html")

    def test_access_denied_to_manager_and_coach_and_director(self):
        for user in [
            self.manager,
            self.coach,
            self.director,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_404_when_measurement_not_found(self):
        self.client.login(username="player", password="pass1234")
        url = reverse("approvals:player_approve", kwargs={"measurement_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_player_can_approve_and_status_updates(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.post(
            self.url, {"status": "approved", "comment": "問題ありません"}
        )

        self.measurement.refresh_from_db()
        self.assertRedirects(response, reverse("home"))

        approval = MeasurementApproval.objects.get(measurement=self.measurement)
        self.assertEqual(approval.status, "approved")
        self.assertEqual(approval.approver, self.player)
        self.assertEqual(approval.role, "player")
        self.assertEqual(approval.step, "self")
        self.assertEqual(self.measurement.status, "player_approved")

    def test_player_can_reject_and_status_becomes_rejected(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.post(
            self.url, {"status": "rejected", "comment": "問題があります"}
        )

        self.measurement.refresh_from_db()
        self.assertEqual(self.measurement.status, "rejected")

    def test_context_contains_measurement(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.get(self.url)
        self.assertIn("m", response.context)
        self.assertEqual(response.context["m"], self.measurement)

    def test_other_player_cannot_access_view(self):
        self.client.login(username="other_player", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)  # 権限がないのでForbidden


class TestCoachPendingApprovalListView(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )

        self.measurement = Measurement.objects.create(
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

        self.url = reverse("approvals:coach_pending_approvals")

        MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.player,
            role="player",
            step="self",
            status="approved",
        )

    def test_coach_can_access_and_see_measurements(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        measurements = response.context["measurements"]
        self.assertIn(self.measurement, measurements)

    def test_manager_cannot_access(self):
        self.client.login(username="manager", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_only_unapproved_measurements_shown(self):
        self.client.login(username="coach", password="pass1234")

        # 承認済みの承認履歴を作る
        self.approval = MeasurementApproval.objects.create(
            measurement=self.measurement,
            approver=self.coach,
            role="coach",
            step="coach",
            status="approved",
        )

        response = self.client.get(self.url)
        measurements = response.context["measurements"]

        # もう承認済みだから一覧に表示されない
        self.assertNotIn(self.measurement, measurements)


class TestCoachApprovalCreateView(TestCase):
    def setUp(self):
        self.player = User.objects.create_user(
            username="player", password="pass1234", role="player"
        )
        self.manager = User.objects.create_user(
            username="manager", password="pass1234", role="manager"
        )
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )

        self.measurement = Measurement.objects.create(
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

        self.url = reverse(
            "approvals:coach_approve",
            kwargs={"measurement_id": self.measurement.id},
        )

    def test_anonymous_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_uses_correct_template(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "approvals/coach_approval_form.html")

    def test_access_denied_to_manager_and_player_and_director(self):
        for user in [
            self.manager,
            self.player,
            self.director,
        ]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 403)
            self.client.logout()

    def test_404_when_measurement_not_found(self):
        self.client.login(username="coach", password="pass1234")
        url = reverse("approvals:coach_approve", kwargs={"measurement_id": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_coach_can_approve_and_status_updates(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.post(
            self.url, {"status": "approved", "comment": "問題ありません"}
        )

        self.measurement.refresh_from_db()
        self.assertRedirects(response, reverse("home"))

        approval = MeasurementApproval.objects.get(measurement=self.measurement)
        self.assertEqual(approval.status, "approved")
        self.assertEqual(approval.approver, self.coach)
        self.assertEqual(approval.role, "coach")
        self.assertEqual(approval.step, "coach")
        self.assertEqual(self.measurement.status, "coach_approved")

    def test_coach_can_reject_and_status_becomes_rejected(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.post(
            self.url, {"status": "rejected", "comment": "問題があります"}
        )

        self.measurement.refresh_from_db()
        self.assertEqual(self.measurement.status, "rejected")

    def test_context_contains_measurement(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(self.url)
        self.assertIn("m", response.context)
        self.assertEqual(response.context["m"], self.measurement)
