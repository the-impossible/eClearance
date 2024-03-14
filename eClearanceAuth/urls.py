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

    #Admin-------> offices
    path('manage_offices', ManageOfficeView.as_view(), name="manage_offices"),
    path('update_office/<str:pk>', UpdateAdministrativeOfficeView.as_view(), name="update_office"),
    path('delete_office/<str:pk>', DeleteAdministrativeOfficeView.as_view(), name="delete_office"),

    #Student-------> clearance
    path('manage_clearance', ApplyClearanceView.as_view(), name="manage_clearance"),
    path('update_student_profile/<str:pk>', UpdateStudentProfileView.as_view(), name="update_student_profile"),
    path('print_clearance', PrintClearanceView.as_view(), name="print_clearance"),


    #Office-------> clearance
    path('clearance_application', ClearanceApplicationView.as_view(), name="clearance_application"),
    path('disapproved_application', DisapprovedApplicationView.as_view(), name="disapproved_application"),

    path('change_password/<str:pk>',
         ChangePassword.as_view(), name="change_password"),
]
