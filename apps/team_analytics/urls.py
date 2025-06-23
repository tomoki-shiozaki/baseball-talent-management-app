from django.urls import path

from apps.team_analytics.views import DashboardView

app_name = "team_analytics"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
