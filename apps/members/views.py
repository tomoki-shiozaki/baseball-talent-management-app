from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView, FormView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.members.forms import TeamMemberCreateForm, TeamMemberRetireForm

User = get_user_model()


# Create your views here.
class TeamMemberListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = "members/team_member_list.html"
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_coach or self.request.user.is_director

    def get_queryset(self):
        status_filter = self.request.GET.get("status", "active")  # デフォルトは在籍中
        role_filter = self.request.GET.get("role", "player")  # デフォルトは部員
        qs = User.objects.filter(status=status_filter, role=role_filter)

        return qs.order_by("grade")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在のフィルター値をテンプレートに渡す（ページネーションのリンク用など）
        context["current_role"] = self.request.GET.get("role", "player")
        context["current_status"] = self.request.GET.get("status", "active")
        return context


class TeamMemberCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = User
    form_class = TeamMemberCreateForm
    template_name = "members/team_member_new.html"
    success_url = reverse_lazy("members:team_member_list")

    def test_func(self):
        return self.request.user.is_coach or self.request.user.is_director


class TeamMemberRetireView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "members/team_member_retire_confirm.html"
    form_class = TeamMemberRetireForm
    success_url = reverse_lazy("members:team_member_list")

    def dispatch(self, request, *args, **kwargs):
        self.member = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_coach or self.request.user.is_director

    def form_valid(self, form):
        # 退部処理
        self.member.status = "retired"
        self.member.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.member
        return context
