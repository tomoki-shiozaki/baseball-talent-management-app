from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TestTeamMemberListView(TestCase):
    def setUp(self):
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
        self.url = reverse("members:team_member_list")

    def test_access_denied_for_non_coach_or_director(self):
        self.client.login(username="player", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_access_granted_for_coach_or_director(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_queryset_filters_only_players(self):
        self.client.login(username="director", password="pass1234")
        response = self.client.get(self.url)
        users = response.context["object_list"]
        self.assertIn(self.player, users)
        self.assertNotIn(self.manager, users)


class TestTeamMemberCreateView(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.director = User.objects.create_user(
            username="director", password="pass1234", role="director"
        )
        self.other = User.objects.create_user(
            username="other", password="pass1234", role="player"
        )  # アクセス不可

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("members:team_member_new"))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response, f"/accounts/login/?next={reverse('members:team_member_new')}"
        )

    def test_logged_in_user_can_access(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(reverse("members:team_member_new"))
        self.assertEqual(response.status_code, 200)

    def test_access_denied_for_non_coach_director(self):
        self.client.login(username="other", password="pass1234")
        response = self.client.get(reverse("members:team_member_new"))
        self.assertEqual(response.status_code, 403)

    def test_access_granted_for_coach_or_director(self):
        for user in [self.coach, self.director]:
            self.client.login(username=user.username, password="pass1234")
            response = self.client.get(reverse("members:team_member_new"))
            self.assertEqual(response.status_code, 200)
            self.client.logout()

    def test_valid_form_creates_user(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.post(
            reverse("members:team_member_new"),
            {
                "username": "newplayer",
                "password1": "securepass123",
                "password2": "securepass123",
                "role": "player",
            },
        )
        self.assertRedirects(response, reverse("members:team_member_list"))
        self.assertTrue(User.objects.filter(username="newplayer").exists())


class TestTeamMemberRetireView(TestCase):
    def setUp(self):
        self.coach = User.objects.create_user(
            username="coach", password="pass1234", role="coach"
        )
        self.other = User.objects.create_user(
            username="other", password="pass1234", role="player"
        )
        self.member = User.objects.create_user(
            username="member", password="pass1234", role="player", status="active"
        )
        self.url = reverse("members:team_member_retire", kwargs={"pk": self.member.pk})

    def test_access_denied_if_not_coach_or_director(self):
        self.client.login(username="other", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_renders_template_and_context(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "members/team_member_retire_confirm.html")
        self.assertEqual(response.context["member"], self.member)

    def test_post_retire_changes_status_and_redirects(self):
        self.client.login(username="coach", password="pass1234")
        response = self.client.post(self.url, data={"confirm": True})
        self.assertRedirects(response, reverse("members:team_member_list"))
        self.member.refresh_from_db()
        self.assertEqual(self.member.status, "retired")
