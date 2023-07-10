from django.urls import path
from eClearanceAuth.views import *

app_name = "auth"

urlpatterns = [
    # Basic
    path('', HomePageView.as_view(), name="home"),
    # Auth
    path('login', LoginPageView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),

    path('dashboard', DashboardView.as_view(), name="dashboard"),
]
