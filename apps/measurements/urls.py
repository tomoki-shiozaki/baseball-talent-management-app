from django.urls import path

from apps.measurements.views import (
    MeasurementCreateView,
    PlayerListView,
    MyMeasurementListView,
    MemberListView,
    PlayerMeasurementListView,
)

app_name = "measurements"

urlpatterns = [
    # マネージャー用。測定結果入力
    path(
        "players/<int:player_id>/new/",
        MeasurementCreateView.as_view(),
        name="new",
    ),
    path("players/", PlayerListView.as_view(), name="player_list"),
    # 部員用。自分の測定結果閲覧
    path(
        "my-records",
        MyMeasurementListView.as_view(),
        name="my_records",
    ),
    # コーチと監督用。部員の測定結果閲覧
    path(
        "members",
        MemberListView.as_view(),
        name="member_list",
    ),
    path(
        "members/<int:player_id>/records/",
        PlayerMeasurementListView.as_view(),
        name="player_measurement_list",
    ),
]
