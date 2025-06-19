from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View

from apps.measurements.models import Measurement
from apps.approvals.models import MeasurementApproval


# Create your views here.
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            if user.is_manager:
                rejected_count = Measurement.objects.filter(
                    created_by=user,
                    status="rejected",  # マネージャーが作成した記録に対して
                    recreated_at__isnull=True,  # 再作成されていないものだけカウント
                ).count()
                context["rejected_count"] = rejected_count

            # 部員の未承認記録の数をホーム画面に通知する
            elif user.is_player:
                pending_count = Measurement.objects.filter(
                    status="pending", player=user
                ).count()
                context["pending_count"] = pending_count

            # コーチの未承認記録の数をホーム画面に通知する
            elif user.is_coach:
                # コーチが承認すべき未承認記録（部員が承認済だがコーチ未承認）
                pending_count = Measurement.objects.filter(
                    status="player_approved",
                ).count()
                context["coach_pending_count"] = pending_count

            return context
