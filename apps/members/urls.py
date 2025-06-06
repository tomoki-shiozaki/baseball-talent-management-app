from django.urls import path

from apps.members.views import TeamMemberListView, TeamMemberCreateView

app_name = "members"

urlpatterns = [
    path(
        "team-members/",
        TeamMemberListView.as_view(),
        name="team_member_list",
    ),
    path("team-members/new/", TeamMemberCreateView.as_view(), name="team_member_new"),
]
