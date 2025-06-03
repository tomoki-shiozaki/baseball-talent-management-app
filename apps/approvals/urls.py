from django.urls import path

from apps.approvals.views import PendingApprovalListView

app_name = "approvals"

urlpatterns = [
    # 部員用。自分の測定結果の承認
    path(
        "approvals/",
        PendingApprovalListView.as_view(),
        name="pending",
    ),
]
