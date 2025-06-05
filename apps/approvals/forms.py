from django import forms
from apps.measurements.models import Measurement


class MeasurementForm(forms.ModelForm):
    class Meta:
        model = Measurement
        fields = [
            "date",
            "sprint_50m",
            "base_running",
            "long_throw",
            "straight_ball_speed",
            "hit_ball_speed",
            "swing_speed",
            "bench_press",
            "squat",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "date": "測定日",
            "sprint_50m": "50m走（秒）",
            "base_running": "ベースランニング（秒）",
            "long_throw": "遠投（m）",
            "straight_ball_speed": "ストレート球速（km/h）",
            "hit_ball_speed": "打球速度（km/h）",
            "swing_speed": "スイング速度（km/h）",
            "bench_press": "ベンチプレス（kg）",
            "squat": "スクワット（kg）",
        }
        help_texts = {
            "date": "日付を YYYY-MM-DD の形式で入力してください。例: 2025-01-01",
            "sprint_50m": "50m走のタイム（秒）を入力してください",
            "base_running": "ベースランニングのタイム（秒）を入力してください",
            "long_throw": "遠投距離（メートル）を入力してください",
            "straight_ball_speed": "ストレートの球速（km/h）を入力してください",
            "hit_ball_speed": "打球速度（km/h）を入力してください",
            "swing_speed": "スイング速度（km/h）を入力してください",
            "bench_press": "ベンチプレスの重量（kg）を入力してください",
            "squat": "スクワットの重量（kg）を入力してください",
        }
