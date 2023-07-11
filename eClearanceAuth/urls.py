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

    #Admin-------> student
    path('manage_student', ManageStudentView.as_view(), name="manage_student"),
    path('update_student/<str:pk>', UpdateStudentView.as_view(), name="update_student"),
    path('delete_student/<str:pk>', DeleteStudentView.as_view(), name="delete_student"),
]
