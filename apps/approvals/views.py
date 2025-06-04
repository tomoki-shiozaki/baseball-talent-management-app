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
class PlayerPendingApprovalListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = "approvals/pending_approval_list.html"
    context_object_name = "measurements"

    def get_queryset(self):
        user = self.request.user

        if not user.is_player:
            return Measurement.objects.none()

        # 承認履歴に「自分による承認（step=self）」が「済み（承認済または否認）」でないもの
        return (
            Measurement.objects.filter(player=user)
            .exclude(
                approvals__approver=user,
                approvals__step="self",
                approvals__status__in=["approved", "rejected"],
            )
            .select_related("player")
            .distinct()
        )


class PlayerApprovalCreateView(LoginRequiredMixin, CreateView):
    model = MeasurementApproval
    template_name = "approvals/player_approval_form.html"
    fields = ["status", "comment"]  # 承認 or 否認、コメント入力

    def dispatch(self, request, *args, **kwargs):
        self.measurement = get_object_or_404(Measurement, id=kwargs["measurement_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.measurement = self.measurement
        form.instance.approver = self.request.user
        form.instance.role = "player"
        form.instance.step = "self"

        response = super().form_valid(form)

        # Measurementのstatusを更新
        if form.instance.status == "approved":
            self.measurement.status = "player_approved"
        elif form.instance.status == "rejected":
            self.measurement.status = "rejected"
        self.measurement.save()

        return response

    def get_success_url(self):
        return reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["m"] = self.measurement
        return context


class CoachPendingApprovalListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = "approvals/coach_pending_approval_list.html"
    context_object_name = "measurements"

    def get_queryset(self):
        user = self.request.user

        if not user.is_coach:
            return Measurement.objects.none()

        return (
            Measurement.objects.filter(
                approvals__step="self", approvals__status="approved"
            )
            .exclude(
                approvals__approver=user,
                approvals__step="coach",
                approvals__status__in=["approved", "rejected"],
            )
            .select_related("player")
            .distinct()
        )


class CoachApprovalCreateView(LoginRequiredMixin, CreateView):
    model = MeasurementApproval
    template_name = "approvals/coach_approval_form.html"
    fields = ["status", "comment"]  # 承認 or 否認、コメント入力

    def dispatch(self, request, *args, **kwargs):
        self.measurement = get_object_or_404(Measurement, id=kwargs["measurement_id"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.measurement = self.measurement
        form.instance.approver = self.request.user
        form.instance.role = "coach"
        form.instance.step = "coach"

        response = super().form_valid(form)

        # Measurementのstatusを更新
        if form.instance.status == "approved":
            self.measurement.status = "coach_approved"
        elif form.instance.status == "rejected":
            self.measurement.status = "rejected"
        self.measurement.save()

        return response

    def get_success_url(self):
        return reverse_lazy("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["m"] = self.measurement
        return context
