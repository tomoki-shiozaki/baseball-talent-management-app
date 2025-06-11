from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.measurements.models import Measurement
from apps.approvals.models import MeasurementApproval


# Create your views here.
# マネージャー用
class MeasurementCreateView(LoginRequiredMixin, CreateView):
    model = Measurement
    template_name = "measurements/measurement_form.html"
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
    success_url = reverse_lazy("measurements:player_list")

    def dispatch(self, request, *args, **kwargs):
        # URLのplayer_idから部員（プレイヤー）を取得
        self.player = get_object_or_404(
            get_user_model(), id=kwargs["player_id"], role="player"
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.player = self.player
        form.instance.status = "pending"  # 測定記録は承認待ちとして保存
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["player"] = self.player  # テンプレートで使えるように
        return context


class PlayerListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = "measurements/player_list.html"
    context_object_name = "players"

    def get_queryset(self):
        return get_user_model().objects.filter(role="player", status="active")


# 部員用
class MyMeasurementListView(LoginRequiredMixin, ListView):
    model = Measurement
    template_name = "measurements/my_measurement_list.html"
    context_object_name = "measurements"

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.GET.get(
            "status", "approved"
        )  # デフォルトは確定済み
        qs = Measurement.objects.filter(player=user)

        if status_filter == "approved":
            qs = qs.filter(status="coach_approved")
        elif status_filter == "pending":
            qs = qs.filter(status__in=["pending", "player_approved"])
        elif status_filter == "rejected":
            qs = qs.filter(status="rejected")
        else:
            qs = qs.none()

        # 指定がない場合は "desc"（新しい順）をデフォルトにする。
        order = self.request.GET.get("order", "desc")
        ordering = "-date" if order == "desc" else "date"
        return qs.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        full_name = user.get_full_name()
        # ログインユーザーの姓名をコンテキストに追加
        context["player_name"] = full_name if full_name else user.username
        context["current_order"] = self.request.GET.get("order", "desc")
        context["current_status"] = self.request.GET.get("status", "approved")
        return context


# コーチ・監督用
class MemberListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = get_user_model()
    template_name = "measurements/member_list.html"
    context_object_name = "players"

    def test_func(self):
        # コーチ・監督のみアクセスOKにする
        return self.request.user.role in ["coach", "director"]

    def get_queryset(self):
        return get_user_model().objects.filter(role="player", status="active")


class PlayerMeasurementListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Measurement
    template_name = "measurements/player_measurement_list.html"
    context_object_name = "measurements"

    def test_func(self):
        return self.request.user.role in ["coach", "director"]

    def get_queryset(self):
        player_id = self.kwargs.get("player_id")
        status_filter = self.request.GET.get(
            "status", "approved"
        )  # デフォルトは確定済み
        qs = Measurement.objects.filter(player_id=player_id)

        if status_filter == "approved":
            qs = qs.filter(status="coach_approved")
        elif status_filter == "pending":
            qs = qs.filter(status__in=["pending", "player_approved"])
        elif status_filter == "rejected":
            qs = qs.filter(status="rejected")
        else:
            qs = qs.none()

        # 指定がない場合は "desc"（新しい順）をデフォルトにする。
        order = self.request.GET.get("order", "desc")
        ordering = "-date" if order == "desc" else "date"
        return qs.order_by(ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        player_id = self.kwargs.get("player_id")
        player = get_object_or_404(get_user_model(), id=player_id)
        full_name = player.get_full_name()
        # ログインユーザーのユーザー名をコンテキストに追加
        context["player_name"] = full_name if full_name else player.username
        context["current_order"] = self.request.GET.get("order", "desc")
        context["current_status"] = self.request.GET.get("status", "approved")
        return context
