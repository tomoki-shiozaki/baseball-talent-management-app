from django.test import TestCase

from apps.members.forms import TeamMemberCreateForm, TeamMemberRetireForm
from apps.accounts.models import CustomUser


class TestTeamMemberCreateForm(TestCase):
    def test_role_choices_are_limited(self):
        form = TeamMemberCreateForm()
        allowed_roles = {"player", "manager"}
        # フィールドの選択肢がallowed_rolesに限定されているか
        roles_in_form = {choice[0] for choice in form.fields["role"].choices}
        self.assertTrue(roles_in_form.issubset(allowed_roles))

    def test_valid_data(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "role": "player",
            "grade": "3",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = TeamMemberCreateForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_role(self):
        data = {
            "username": "testuser2",
            "email": "test2@example.com",
            "first_name": "Test2",
            "last_name": "User2",
            "role": "admin",  # 許可されていないrole
            "grade": "2",
            "password1": "complexpassword123",
            "password2": "complexpassword123",
        }
        form = TeamMemberCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("role", form.errors)


class TestTeamMemberRetireForm(TestCase):
    def test_confirm_required(self):
        form = TeamMemberRetireForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("confirm", form.errors)

    def test_confirm_true(self):
        form = TeamMemberRetireForm(data={"confirm": True})
        self.assertTrue(form.is_valid())
