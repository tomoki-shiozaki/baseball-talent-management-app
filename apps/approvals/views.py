from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView, DetailView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from apps.approvals.models import MeasurementApproval
from apps.measurements.models import Measurement


# Create your views here.
class RejectedApprovalListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = MeasurementApproval
    template_name = "approvals/manager_rejected_approval_list.html"
    context_object_name = "approvals"

    def test_func(self):
        # マネージャー権限のみ閲覧可能にする
        return self.request.user.is_manager

    def get_queryset(self):
        # 否認された承認記録のうち、まだ再作成されていないものを取得
        return (
            MeasurementApproval.objects.filter(
                measurement__created_by=self.request.user,
                status="rejected",
                measurement__recreated_at__isnull=True,  # 再作成されていない記録のみ
            )
            .select_related("measurement", "approver")
            .order_by("-created_at")
        )


class RejectedApprovalDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = MeasurementApproval
    template_name = "approvals/manager_rejected_approval_detail.html"
    context_object_name = "approval"

    def test_func(self):
        # マネージャーのみ
        return self.request.user.is_manager


class MeasurementRecreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Measurement
    template_name = "approvals/manager_measurement_form.html"
    fields = (
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

    def test_func(self):
        return self.request.user.is_manager

    def dispatch(self, request, *args, **kwargs):
        self.approval = get_object_or_404(MeasurementApproval, pk=kwargs["approval_pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        original = self.approval.measurement
        initial = {
            "date": original.date,
            "sprint_50m": original.sprint_50m,
            "base_running": original.base_running,
            "long_throw": original.long_throw,
            "straight_ball_speed": original.straight_ball_speed,
            "hit_ball_speed": original.hit_ball_speed,
            "swing_speed": original.swing_speed,
            "bench_press": original.bench_press,
            "squat": original.squat,
        }
        return initial

    def form_valid(self, form):
        # 作成者は現在のユーザー（マネージャー）で固定する
        form.instance.created_by = self.request.user
        form.instance.player = self.approval.measurement.player
        form.instance.status = "pending"

        # 保存前に、古いレコードに再作成日時を記録
        original = self.approval.measurement
        original.recreated_at = timezone.now()
        original.save(update_fields=["recreated_at"])

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # approvalオブジェクトをテンプレートに渡す
        context["approval"] = self.approval
        return context

    def get_success_url(self):
        return reverse_lazy("home")


class PlayerPendingApprovalListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Measurement
    template_name = "approvals/player_pending_approval_list.html"
    context_object_name = "measurements"

    def test_func(self):
        # プレイヤーのみアクセス可能にする
        return self.request.user.is_player

    def get_queryset(self):
        user = self.request.user

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


class PlayerApprovalCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MeasurementApproval
    template_name = "approvals/player_approval_form.html"
    fields = ["status", "comment"]  # 承認 or 否認、コメント入力

    def test_func(self):
        # プレイヤーのみアクセス可能にする
        return self.request.user.is_player

    def dispatch(self, request, *args, **kwargs):
        self.measurement = get_object_or_404(Measurement, id=kwargs["measurement_id"])
        # ログインユーザーが対象のプレイヤーであることを確認
        if self.measurement.player != request.user:
            return self.handle_no_permission()  # 403 Forbiddenを返す
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


class CoachPendingApprovalListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Measurement
    template_name = "approvals/coach_pending_approval_list.html"
    context_object_name = "measurements"

    def test_func(self):
        return self.request.user.is_coach

    def get_queryset(self):
        user = self.request.user

        return (
            Measurement.objects.filter(
                recreated_at__isnull=True,
                approvals__step="self",
                approvals__status="approved",
            )
            .exclude(
                approvals__step="coach",
                approvals__status__in=["approved", "rejected"],
            )
            .select_related("player")
            .distinct()
        )


class CoachApprovalCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MeasurementApproval
    template_name = "approvals/coach_approval_form.html"
    fields = ["status", "comment"]  # 承認 or 否認、コメント入力

    def test_func(self):
        return self.request.user.is_coach

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
