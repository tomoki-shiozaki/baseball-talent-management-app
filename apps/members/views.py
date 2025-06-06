from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from apps.members.forms import TeamMemberCreateForm

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
