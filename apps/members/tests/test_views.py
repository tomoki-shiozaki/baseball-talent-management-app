from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class TeamMemberListViewTests(TestCase):
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

    def test_queryset_filters_only_players_and_managers(self):
        self.client.login(username="director", password="pass1234")
        response = self.client.get(self.url)
        users = response.context["object_list"]
        self.assertIn(self.player, users)
        self.assertIn(self.manager, users)
