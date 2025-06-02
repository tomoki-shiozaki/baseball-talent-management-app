from django.urls import path

from apps.measurements.views import MeasurementCreateView

app_name = "measurements"

urlpatterns = [
    path(
        "new/",
        MeasurementCreateView.as_view(),
        name="new",
    ),
]
