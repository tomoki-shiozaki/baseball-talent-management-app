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
class TeamMemberListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "members/team_member_list.html"
    paginate_by = 10

    def get_queryset(self):
        return User.objects.filter(role__in=["player", "manager"])


class TeamMemberCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = TeamMemberCreateForm
    template_name = "members/team_member_new.html"
    success_url = reverse_lazy("members:team_member_list")


class TeamMemberRetireView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "members/team_member_retire_confirm.html"
    form_class = TeamMemberRetireForm
    success_url = reverse_lazy("members:team_member_list")

    def dispatch(self, request, *args, **kwargs):
        self.member = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        return self.request.user.is_coach or self.request.user.director

    def form_valid(self, form):
        # 退部処理
        self.member.status = "retired"
        self.member.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["member"] = self.member
        return context
