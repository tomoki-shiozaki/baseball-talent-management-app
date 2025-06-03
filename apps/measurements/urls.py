from django.urls import path

from apps.measurements.views import (
    MeasurementCreateView,
    PlayerListView,
    MeasurementListView,
)

app_name = "measurements"

urlpatterns = [
    # 測定結果入力
    path(
        "players/<int:player_id>/new/",
        MeasurementCreateView.as_view(),
        name="new",
    ),
    path("players/", PlayerListView.as_view(), name="player_list"),
    # 測定結果閲覧
    path(
        "list/",
        MeasurementListView.as_view(),
        name="list",
    ),
]
