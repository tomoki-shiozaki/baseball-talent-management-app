from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView

from apps.measurements.models import Measurement


# Create your views here.
class MeasurementCreateView(LoginRequiredMixin, CreateView):
    model = Measurement
    template_name = "measurements/measurement_form.html"
    fields = (
        "player",
        "date",
        "sprint_50m",
        "base_running",
        "long_throw",
        "straight_ball_speed",
        "hit_ball_speed",
        "swing_speed",
        "bench_press",
        "squat",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
