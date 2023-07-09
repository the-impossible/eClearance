from django.shortcuts import render
from django.views.generic import TemplateView, CreateView, UpdateView

# Create your views here.


class HomePageView(TemplateView):
    template_name = "frontend/index.html"

class DashboardView(TemplateView):
    template_name = "backend/dashboard.html"
