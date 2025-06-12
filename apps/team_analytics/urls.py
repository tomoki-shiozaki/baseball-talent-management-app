from django.urls import path

from apps.team_analytics import views

app_name = "team_analytics"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    # path(
    #     "sprint-50m-monthly/",
    #     views.sprint_50m_monthly_avg,
    #     name="sprint_50m_monthly_avg",
    # ),
]
