from django.shortcuts import render
from django.views.generic import ListView, DetailView
from report.models import Twitter_user
from report.models import Twitter_user_stats

# Create your views here.


class TwitterUserListView(ListView):
    model = Twitter_user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_stats"] = Twitter_user_stats.objects.all()
        return context


class TwitterUserStatsView(DetailView):

    model = Twitter_user
    template_name = 'report/detail.html'
