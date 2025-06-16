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
    path("dashboard/2/", views.dashboard_overview, name="dashboard_overview"),
    path("dashboard/3/", views.dashboard3, name="dashboard3"),
    path("sprint/", views.sprint_detail, name="sprint_detail"),
    path("hitting/", views.hitting_detail, name="hitting_detail"),
    path("strength/", views.strength_detail, name="strength_detail"),
]
