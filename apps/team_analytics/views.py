from django.db.models.functions import TruncMonth
from django.db.models import Avg, Max, Min
from django.shortcuts import render

from apps.measurements.models import Measurement


# Create your views here.
def dashboard(request):
    # 50m走の月別平均
    sprint_data = (
        Measurement.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(avg_sprint=Avg("sprint_50m"))
        .order_by("month")
    )
    sprint_labels = [entry["month"].strftime("%Y-%m") for entry in sprint_data]
    sprint_values = [round(entry["avg_sprint"], 2) for entry in sprint_data]

    # 球速の平均・最大・最小
    ball_stats = Measurement.objects.aggregate(
        avg_speed=Avg("straight_ball_speed"),
        max_speed=Max("straight_ball_speed"),
        min_speed=Min("straight_ball_speed"),
    )

    context = {
        "sprint_labels": sprint_labels,
        "sprint_values": sprint_values,
        "ball_stats": ball_stats,
    }
    return render(request, "team_analytics/dashboard.html", context)


def sprint_50m_monthly_avg(request):
    # 月ごとの50m走平均タイムを計算
    data = (
        Measurement.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(avg_time=Avg("sprint_50m"))
        .order_by("month")
    )

    # グラフ用に日付と平均タイムをリストに加工
    labels = [entry["month"].strftime("%Y-%m") for entry in data]
    values = [round(entry["avg_time"], 2) for entry in data]

    context = {
        "labels": labels,
        "values": values,
    }
    return render(request, "team_analytics/sprint_50m_monthly_avg.html", context)
