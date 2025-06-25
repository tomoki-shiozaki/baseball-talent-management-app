from collections import defaultdict
from typing import Dict
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models.functions import TruncMonth
from django.shortcuts import render, get_object_or_404

from apps.measurements.models import Measurement
from apps.team_analytics.utils import calc_avg

User = get_user_model()


# Create your views here.
class PlayerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/player_dashboard.html"

    def test_func(self):
        return self.request.user.is_player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["player"] = user

        measurement_fields = {
            "50m走": "sprint_50m",
            "ベースラン": "base_running",
            "遠投": "long_throw",
            "ストレート球速": "straight_ball_speed",
            "打球速度": "hit_ball_speed",
            "スイング速度": "swing_speed",
            "ベンチプレス": "bench_press",
            "スクワット": "squat",
        }

        # 個人記録取得
        player_qs = (
            Measurement.objects.filter(status="coach_approved", player=user)
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )

        # 月別データ構築
        player_data: Dict[str, Dict[date, float]] = {}
        months_in_order = []

        for row in player_qs:
            month = row["month"]
            if month not in months_in_order:
                months_in_order.append(month)
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    if label not in player_data:
                        player_data[label] = {}
                    player_data[label][month] = value

        # 過去7回分のみ使用
        recent_months = months_in_order[-7:]
        labels = [m.strftime("%Y-%m") for m in recent_months]

        # グラフ用データ整形
        measurement_values = {
            label: [player_data[label].get(m, None) for m in recent_months]
            for label in measurement_fields
        }

        context.update(
            {
                "labels": labels,
                "measurement_values": measurement_values,
            }
        )
        return context


class PlayerComparisonView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/player_comparison.html"

    def test_func(self):
        return self.request.user.is_player

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["player"] = user

        measurement_fields = {
            "50m走": "sprint_50m",
            "ベースラン": "base_running",
            "遠投": "long_throw",
            "ストレート球速": "straight_ball_speed",
            "打球速度": "hit_ball_speed",
            "スイング速度": "swing_speed",
            "ベンチプレス": "bench_press",
            "スクワット": "squat",
        }

        # チーム平均取得
        team_qs = (
            Measurement.objects.filter(status="coach_approved")
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )
        team_data = {label: defaultdict(list) for label in measurement_fields}
        for row in team_qs:
            month = row["month"]
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    team_data[label][month].append(value)

        from apps.team_analytics.utils import calc_avg

        team_avg = {
            label: calc_avg(data_dict) for label, data_dict in team_data.items()
        }

        # 個人記録取得
        player_qs = (
            Measurement.objects.filter(status="coach_approved", player=user)
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )

        player_data = {label: {} for label in measurement_fields}
        for row in player_qs:
            month = row["month"]
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    # 各月に1件のみ → 単一値として格納
                    player_data[label][month] = value

        # 共通の月リスト（過去7回分）
        all_months = sorted(set().union(*[avg.keys() for avg in team_avg.values()]))
        recent_months = all_months[-7:]
        labels = [m.strftime("%Y-%m") for m in recent_months]

        # グラフ用に値の配列を整形
        team_values = {
            label: [team_avg[label].get(m, None) for m in recent_months]
            for label in measurement_fields
        }
        player_values = {
            label: [player_data[label].get(m, None) for m in recent_months]
            for label in measurement_fields
        }

        context.update(
            {
                "labels": labels,
                "team_values": team_values,
                "player_values": player_values,
            }
        )

        return context


class StaffDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/staff_dashboard.html"

    def test_func(self):
        return self.request.user.role in ["coach", "director"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1. 種目を一覧で定義
        measurement_fields = {
            "50m走": "sprint_50m",
            "ベースラン": "base_running",
            "遠投": "long_throw",
            "ストレート球速": "straight_ball_speed",
            "打球速度": "hit_ball_speed",
            "スイング速度": "swing_speed",
            "ベンチプレス": "bench_press",
            "スクワット": "squat",
        }

        # 2. クエリで全ての必要フィールドを取得
        qs = (
            Measurement.objects.filter(status="coach_approved")
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )

        # 3. defaultdict で種目ごとのデータをまとめる
        measurement_data = {label: defaultdict(list) for label in measurement_fields}

        for row in qs:
            month = row["month"]
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    measurement_data[label][month].append(value)

        # 4. 月ごとの平均を計算
        measurement_avg = {
            label: calc_avg(data_dict) for label, data_dict in measurement_data.items()
        }

        # 5. X軸（月）の統一
        all_months = sorted(
            set().union(*[avg.keys() for avg in measurement_avg.values()])
        )
        # 前年の同時期までのデータを取得する。7回分あればよい。
        recent_months = sorted(all_months)[-7:]
        labels = [m.strftime("%Y-%m") for m in recent_months]

        # 6. 種目ごとの値リストを整形
        measurement_values = {
            label: [avg.get(m, None) for m in recent_months]
            for label, avg in measurement_avg.items()
        }

        context.update(
            {
                "labels": labels,
                "measurement_values": measurement_values,
            }
        )
        return context


class StaffComparisonEntryView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/staff_comparison_entry.html"

    def test_func(self):
        return self.request.user.role in ["coach", "director"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["players"] = User.objects.filter(
            role="player", is_active=True
        ).order_by("grade", "last_name", "first_name")
        return context


# 部員比較グラフ用ビュー
class StaffPlayerComparisonView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/staff_player_comparison.html"

    def test_func(self):
        return self.request.user.role in ["coach", "director"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        player_id = self.request.GET.get("player_id")
        player = get_object_or_404(User, pk=player_id, role="player", is_active=True)
        context["player"] = player
        context["player_list"] = User.objects.filter(
            role="player", is_active=True
        ).order_by("grade", "last_name", "first_name")

        measurement_fields = {
            "50m走": "sprint_50m",
            "ベースラン": "base_running",
            "遠投": "long_throw",
            "ストレート球速": "straight_ball_speed",
            "打球速度": "hit_ball_speed",
            "スイング速度": "swing_speed",
            "ベンチプレス": "bench_press",
            "スクワット": "squat",
        }

        # チーム平均取得
        team_qs = (
            Measurement.objects.filter(status="coach_approved")
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )
        team_data = {label: defaultdict(list) for label in measurement_fields}
        for row in team_qs:
            month = row["month"]
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    team_data[label][month].append(value)

        from apps.team_analytics.utils import calc_avg

        team_avg = {
            label: calc_avg(data_dict) for label, data_dict in team_data.items()
        }

        # 個人記録取得
        player_qs = (
            Measurement.objects.filter(status="coach_approved", player=player)
            .annotate(month=TruncMonth("date"))
            .values("month", *measurement_fields.values())
            .order_by("month")
        )

        player_data = {label: {} for label in measurement_fields}
        for row in player_qs:
            month = row["month"]
            for label, field in measurement_fields.items():
                value = row.get(field)
                if value is not None:
                    # 各月に1件のみ → 単一値として格納
                    player_data[label][month] = value

        # 共通の月リスト（過去7回分）
        all_months = sorted(set().union(*[avg.keys() for avg in team_avg.values()]))
        recent_months = all_months[-7:]
        labels = [m.strftime("%Y-%m") for m in recent_months]

        # グラフ用に値の配列を整形
        team_values = {
            label: [team_avg[label].get(m, None) for m in recent_months]
            for label in measurement_fields
        }
        player_values = {
            label: [player_data[label].get(m, None) for m in recent_months]
            for label in measurement_fields
        }

        context.update(
            {
                "labels": labels,
                "team_values": team_values,
                "player_values": player_values,
            }
        )

        return context
