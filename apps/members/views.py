from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


# Create your views here.
class MemberListView(LoginRequiredMixin, ListView):
    model = get_user_model()
    template_name = "members/member_list.html"

    def get_queryset(self):
        return get_user_model().objects.filter(role="player")
