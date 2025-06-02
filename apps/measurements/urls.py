from django.urls import path

from apps.measurements.views import MeasurementCreateView, PlayerListView

app_name = "measurements"

urlpatterns = [
    path(
        "players/<int:player_id>/new/",
        MeasurementCreateView.as_view(),
        name="new",
    ),
    path("players/", PlayerListView.as_view(), name="player_list"),
]
