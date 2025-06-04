from django.urls import path

from apps.approvals.views import PendingApprovalListView, PlayerApprovalCreateView

app_name = "approvals"

urlpatterns = [
    # 部員用。自分の測定結果の承認
    path(
        "pending/",
        PendingApprovalListView.as_view(),
        name="pending",
    ),
    path(
        "player/approve/<int:measurement_id>/",
        PlayerApprovalCreateView.as_view(),
        name="player_approve",
    ),
]
