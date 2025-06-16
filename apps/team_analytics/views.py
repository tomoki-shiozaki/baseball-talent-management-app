from collections import defaultdict
from django.db.models.functions import TruncMonth
from django.db.models import Avg, Max, Min
from django.shortcuts import render

from apps.measurements.models import Measurement
from apps.team_analytics.utils import calc_avg


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
    # 1. 種目を一覧で定義
    event_fields = {
        "50m走": "sprint_50m",
        "ベースラン": "base_running",
        "遠投": "long_throw",
    }

    # 2. クエリで全ての必要フィールドを取得
    qs = (
        Measurement.objects.annotate(month=TruncMonth("date"))
        .values("month", *event_fields.values())
        .order_by("month")
    )

    # 3. defaultdict で種目ごとのデータをまとめる
    event_data = {label: defaultdict(list) for label in event_fields}

    for row in qs:
        month = row["month"]
        for label, field in event_fields.items():
            value = row.get(field)
            if value is not None:
                event_data[label][month].append(value)

    # 4. 月ごとの平均を計算
    event_avg = {label: calc_avg(data_dict) for label, data_dict in event_data.items()}

    # 5. X軸（月）の統一
    all_months = sorted(set().union(*[avg.keys() for avg in event_avg.values()]))
    labels = [m.strftime("%Y-%m") for m in all_months]

    # 6. 種目ごとの値リストを整形
    event_values = {
        label: [avg.get(m, None) for m in all_months]
        for label, avg in event_avg.items()
    }

    sprint_values = event_values["50m走"]
    base_running_values = event_values["ベースラン"]
    long_throw_values = event_values["遠投"]

    # # 測定期（年と月）を取得。
    # qs = (
    #     Measurement.objects.annotate(month=TruncMonth("date"))
    #     .values("month", "sprint_50m", "base_running")
    #     .order_by("month")
    # )

    # sprint_data = defaultdict(list)
    # base_running_data = defaultdict(list)

    # for row in qs:
    #     month = row["month"]
    #     sprint_data[month].append(row["sprint_50m"])
    #     base_running_data[month].append(row["base_running"])

    # sprint_avg = calc_avg(sprint_data)
    # base_running_avg = calc_avg(base_running_data)

    # # 共通のX軸
    # # 各種目の平均値辞書をまとめる
    # avg_dicts = [
    #     sprint_avg,
    #     base_running_avg,
    # ]

    # # すべての月をまとめて取得（和集合）
    # all_months = sorted(set().union(*[d.keys() for d in avg_dicts]))
    # labels = [m.strftime("%Y-%m") for m in all_months]
    # sprint_values = [sprint_avg.get(m, None) for m in all_months]
    # base_running_values = [base_running_avg.get(m, None) for m in all_months]

    # # 50m走の月別平均
    # sprint_data = (
    #     Measurement.objects.annotate(month=TruncMonth("date"))
    #     .values("month")
    #     .annotate(avg_sprint=Avg("sprint_50m"))
    #     .order_by("month")
    # )
    # sprint_labels = [entry["month"].strftime("%Y-%m") for entry in sprint_data]
    # sprint_values = [round(entry["avg_sprint"], 2) for entry in sprint_data]

    # base_running_data = (
    #     Measurement.objects.annotate(month=TruncMonth("date"))
    #     .values("month")
    #     .annotate(base_running=Avg("base_running"))
    #     .order_by("month")
    # )
    # base_running_labels = [
    #     entry["month"].strftime("%Y-%m") for entry in base_running_data
    # ]
    # base_running_values = [
    #     round(entry["base_running"], 2) for entry in base_running_data
    # ]

    # 球速の平均・最大・最小
    ball_stats = Measurement.objects.aggregate(
        avg_speed=Avg("straight_ball_speed"),
        max_speed=Max("straight_ball_speed"),
        min_speed=Min("straight_ball_speed"),
    )

    context = {
        "labels": labels,
        "sprint_values": sprint_values,
        "base_running_values": base_running_values,
        "long_throw_values": long_throw_values,
        "ball_stats": ball_stats,
    }
    return render(request, "team_analytics/dashboard3.html", context)
