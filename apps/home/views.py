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
            # 部員の未承認記録の数をホーム画面に通知する
            if user.is_player:
                pending_count = (
                    Measurement.objects.filter(player=user)
                    .exclude(
                        approvals__approver=user,
                        approvals__step="self",
                        approvals__status="approved",
                    )
                    .count()
                )
                context["pending_count"] = pending_count

            # コーチの未承認記録の数をホーム画面に通知する
            elif user.is_coach:
                # コーチが承認すべき未承認記録（部員が承認済だがコーチ未承認）
                pending_count = (
                    Measurement.objects.filter(
                        approvals__step="self", approvals__status="approved"
                    )
                    .exclude(approvals__step="coach", approvals__status="approved")
                    .count()
                )
                context["coach_pending_count"] = pending_count

            return context
