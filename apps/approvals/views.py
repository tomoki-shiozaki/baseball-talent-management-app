from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.approvals.models import MeasurementApproval


# Create your views here.
class PendingApprovalListView(LoginRequiredMixin, ListView):
    model = MeasurementApproval
    template_name = "approvals/pending_approval_list.html"
    context_object_name = "approvals"

    def get_queryset(self):
        return MeasurementApproval.objects.filter(
            approver=self.request.user, status="pending"
        ).select_related("measurement")
