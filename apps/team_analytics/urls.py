from django.urls import path
from .views import (
    PlayerDashboardView,
    PlayerComparisonView,
    StaffDashboardView,
    StaffComparisonEntryView,
    StaffPlayerComparisonView,
)

app_name = "team_analytics"

urlpatterns = [
    # プレイヤー用（選手自身）
    path("player/dashboard/", PlayerDashboardView.as_view(), name="player_dashboard"),
    path(
        "player/comparison/",
        PlayerComparisonView.as_view(),
        name="player_comparison",
    ),
    # スタッフ（コーチ・監督）用
    path("staff/dashboard/", StaffDashboardView.as_view(), name="staff_dashboard"),
    path(
        "staff/comparison/entry/",
        StaffComparisonEntryView.as_view(),
        name="staff_comparison_entry",
    ),
    path(
        "staff/comparison/player/",
        StaffPlayerComparisonView.as_view(),
        name="staff_player_comparison",
    ),
]
