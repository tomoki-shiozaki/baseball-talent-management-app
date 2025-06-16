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
    return render(request, "team_analytics/dashboard_old.html", context)


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


def dashboard_overview(request):
    # 「coach_approved」な測定データの中で最新の日付を取得
    latest_date = Measurement.objects.filter(
        status="coach_approved", player__status="active"
    ).aggregate(latest=Max("date"))["latest"]

    # その最新の日付の測定データを対象に集計
    summary = Measurement.objects.filter(
        status="coach_approved", date=latest_date, player__status="active"
    ).aggregate(
        avg_sprint_50m=Avg("sprint_50m"),
        avg_base_running=Avg("base_running"),
        avg_long_throw=Avg("long_throw"),
        avg_straight_ball_speed=Avg("straight_ball_speed"),
        avg_hit_ball_speed=Avg("hit_ball_speed"),
        avg_swing_speed=Avg("swing_speed"),
        avg_bench_press=Avg("bench_press"),
        avg_squat=Avg("squat"),
    )

    return render(
        request,
        "team_analytics/dashboard_overview.html",
        {"summary": summary, "latest_date": latest_date},
    )


def sprint_detail(request):
    return render(request, "dashboard/sprint_detail.html")


def hitting_detail(request):
    return render(request, "dashboard/hitting_detail.html")


def strength_detail(request):
    return render(request, "dashboard/strength_detail.html")


def dashboard3(request):
    # 50m走の月別平均
    sprint_data = (
        Measurement.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(avg_sprint=Avg("sprint_50m"))
        .order_by("month")
    )
    sprint_labels = [entry["month"].strftime("%Y-%m") for entry in sprint_data]
    sprint_values = [round(entry["avg_sprint"], 2) for entry in sprint_data]

    base_running_data = (
        Measurement.objects.annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(base_running=Avg("base_running"))
        .order_by("month")
    )
    base_running_labels = [
        entry["month"].strftime("%Y-%m") for entry in base_running_data
    ]
    base_running_values = [
        round(entry["base_running"], 2) for entry in base_running_data
    ]

    # 球速の平均・最大・最小
    ball_stats = Measurement.objects.aggregate(
        avg_speed=Avg("straight_ball_speed"),
        max_speed=Max("straight_ball_speed"),
        min_speed=Min("straight_ball_speed"),
    )

    context = {
        "sprint_labels": sprint_labels,
        "sprint_values": sprint_values,
        "base_running_labels": base_running_labels,
        "base_running_values": base_running_values,
        "ball_stats": ball_stats,
    }
    return render(request, "team_analytics/dashboard3.html", context)
