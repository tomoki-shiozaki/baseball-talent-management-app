from django.urls import path

from apps.team_analytics.views import (
    DashboardView,
    ComparisonEntryView,
    PlayerComparisonView,
)

app_name = "team_analytics"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("comparison/entry/", ComparisonEntryView.as_view(), name="comparison_entry"),
    path(
        "comparison/player/",
        PlayerComparisonView.as_view(),
        name="player_comparison",
    ),
]
