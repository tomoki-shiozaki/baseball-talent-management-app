from collections import defaultdict
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from apps.measurements.models import Measurement
from apps.team_analytics.utils import calc_avg


# Create your views here.
class DashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "team_analytics/dashboard.html"

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
        labels = [m.strftime("%Y-%m") for m in all_months]

        # 6. 種目ごとの値リストを整形
        measurement_values = {
            label: [avg.get(m, None) for m in all_months]
            for label, avg in measurement_avg.items()
        }

        context.update(
            {
                "labels": labels,
                "measurement_values": measurement_values,
            }
        )
        return context
