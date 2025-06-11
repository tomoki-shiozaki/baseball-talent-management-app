from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.models import CustomUser


# Create your tests here.
class TestCustomUserModel(TestCase):
    def setUp(self):
        # いろんなroleのユーザーを作る
        self.manager = CustomUser.objects.create(
            username="manager_user", role="manager"
        )
        self.player = CustomUser.objects.create(username="player_user", role="player")
        self.coach = CustomUser.objects.create(username="coach_user", role="coach")
        self.director = CustomUser.objects.create(
            username="director_user", role="director"
        )

    def test_role_properties(self):
        # is_manager
        self.assertTrue(self.manager.is_manager)
        self.assertFalse(self.player.is_manager)
        self.assertFalse(self.coach.is_manager)
        self.assertFalse(self.director.is_manager)

        # is_player
        self.assertTrue(self.player.is_player)
        self.assertFalse(self.manager.is_player)
        self.assertFalse(self.coach.is_player)
        self.assertFalse(self.director.is_player)

        # is_coach
        self.assertTrue(self.coach.is_coach)
        self.assertFalse(self.manager.is_coach)
        self.assertFalse(self.player.is_coach)
        self.assertFalse(self.director.is_coach)

        # is_director
        self.assertTrue(self.director.is_director)
        self.assertFalse(self.manager.is_director)
        self.assertFalse(self.player.is_director)
        self.assertFalse(self.coach.is_director)

    def test_default_status_is_active(self):
        self.assertEqual(self.player.status, "active")
        self.assertEqual(self.manager.status, "active")
        self.assertEqual(self.coach.status, "active")
        self.assertEqual(self.director.status, "active")

    def test_grade_can_be_blank_or_null(self):
        self.assertIsNone(self.player.grade)
