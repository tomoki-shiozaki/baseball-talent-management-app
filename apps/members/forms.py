from apps.accounts.forms import CustomUserCreationForm
from apps.accounts.models import CustomUser


class TeamMemberCreateForm(CustomUserCreationForm):
    class Meta(CustomUserCreationForm.Meta):
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "grade",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # roleの選択肢を部員とマネージャーだけに絞る
        allowed_roles = ["player", "manager"]
        self.fields["role"].choices = [
            (key, label)
            for key, label in CustomUser.ROLE_CHOICES
            if key in allowed_roles
        ]
