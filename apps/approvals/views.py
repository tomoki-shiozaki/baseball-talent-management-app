from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.approvals.models import MeasurementApproval
from apps.measurements.models import Measurement


# Create your views here.
class PendingApprovalListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = "approvals/pending_approval_list.html"
    context_object_name = "measurements"

    def get_queryset(self):
        user = self.request.user

        if user.is_player:
            return (
                Measurement.objects.filter(player=user)
                .exclude(
                    approvals__approver=user,
                    approvals__step="self",
                    approvals__status="approved",
                )
                .select_related("player")
            )

        elif user.is_coach:
            return (
                Measurement.objects.filter(
                    approvals__step="self", approvals__status="approved"
                )
                .exclude(
                    approvals__approver=user,
                    approvals__step="coach",
                    approvals__status="approved",
                )
                .select_related("player")
            )

        else:
            return Measurement.objects.none()  # マネージャー・監督などは対象外
