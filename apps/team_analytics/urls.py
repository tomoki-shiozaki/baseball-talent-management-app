from django.urls import path

from apps.team_analytics import views

app_name = "team_analytics"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
]
