from django.urls import path
from eClearanceAuth.views import *

app_name = "auth"

urlpatterns = [
    path('', HomePageView.as_view(), name="home"),
    # Auth
    path('dashboard', DashboardView.as_view(), name="dashboard"),
]
