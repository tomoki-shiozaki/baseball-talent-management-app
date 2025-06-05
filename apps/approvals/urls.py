from django.urls import path

from apps.approvals.views import (
    RejectedApprovalListView,
    RejectedApprovalDetailView,
    PlayerPendingApprovalListView,
    PlayerApprovalCreateView,
    CoachPendingApprovalListView,
    CoachApprovalCreateView,
)

app_name = "approvals"

urlpatterns = [
    # マネージャー用。否認された承認記録を扱う。
    path(
        "manager/rejected/",
        RejectedApprovalListView.as_view(),
        name="manager_rejected_approval_list",
    ),
    path(
        "manager/rejected/<int:pk>/",
        RejectedApprovalDetailView.as_view(),
        name="manager_rejected_approval_detail",
    ),
    # 部員用。自分の測定結果の承認
    path(
        "player/pending/",
        PlayerPendingApprovalListView.as_view(),
        name="player_pending_approvals",
    ),
    path(
        "player/approve/<int:measurement_id>/",
        PlayerApprovalCreateView.as_view(),
        name="player_approve",
    ),
    # コーチ用。部員の測定結果の承認
    path(
        "coach/pending/",
        CoachPendingApprovalListView.as_view(),
        name="coach_pending_approvals",
    ),
    path(
        "coach/approve/<int:measurement_id>/",
        CoachApprovalCreateView.as_view(),
        name="coach_approve",
    ),
]
