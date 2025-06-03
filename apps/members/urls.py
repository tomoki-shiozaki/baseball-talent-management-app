from django.urls import path

from apps.members.views import MemberListView

app_name = "members"

urlpatterns = [
    path(
        "",
        MemberListView.as_view(),
        name="list",
    ),
]
