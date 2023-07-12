from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password, check_password
from django.views import View
import csv
import io
import codecs
from django.urls import reverse_lazy
from eClearanceAuth.models import *
from eClearanceAuth.forms import *

# Create your views here.

PASSWORD = '12345678'


class HomePageView(TemplateView):
    template_name = "frontend/index.html"


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "backend/dashboard.html"


class LogoutView(LoginRequiredMixin, View):

    def post(self, request):
        logout(request)
        messages.success(
            request, 'You are successfully logged out, to continue login again')
        return redirect('auth:login')


class LoginPageView(View):
    def get(self, request):
        return render(request, 'backend/auth/login.html')

    def post(self, request):
        username = request.POST.get('username').upper().strip()
        password = request.POST.get('password').strip()

        if username and password:
            user = authenticate(request, username=username, password=password)

            if user:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"You are now signed in {user}")

                    nxt = request.GET.get('next', None)
                    if nxt is None:
                        return redirect('auth:dashboard')
                    return redirect(self.request.GET.get('next', None))

                else:
                    messages.warning(
                        request, 'Account not active contact the administrator')
            else:
                messages.error(request, 'Invalid login credentials')
        else:
            messages.error(request, 'All fields are required!!')

        return redirect('auth:login')


class ManageStudentView(LoginRequiredMixin, ListView):
    template_name = "backend/admin/manage_student.html"
    model = StudentProfile
    form_class = CreateSingleStudentForm
    second_form_class = CreateMultipleStudentForm
    queryset = StudentProfile.objects.all().order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form1"] = self.form_class
        context["form2"] = self.second_form_class
        return context

    def post(self, request):

        form1 = self.form_class(request.POST, request.FILES)
        form2 = self.second_form_class(request.POST, request.FILES)

        if 'multiple' in request.POST:

            if form2.is_valid():

                csv_obj = csv.reader(codecs.iterdecode(
                    request.FILES['file'], 'utf-8'))

                objs = []
                sub_objs = []

                session = form2.cleaned_data.get('session')
                programme = form2.cleaned_data.get('programme')
                department = form2.cleaned_data.get('department')
                user_type = UserType.objects.get(user_type="Student")

                for row in csv_obj:
                    objs.append(User(
                        username=row[0].upper(), name=row[1], user_type=user_type, password=make_password(PASSWORD)))

                created_users = User.objects.bulk_create(objs)

                for user in created_users:
                    sub_objs.append(StudentProfile(
                        user=user, department=department, session=session, programme=programme))
                created_user_profiles = StudentProfile.objects.bulk_create(
                    sub_objs)

                messages.success(request, "Students has been created")
            else:

                messages.error(request, form2.errors.as_text())

                return render(request, 'backend/admin/manage_student.html',

                              context={
                                  'form1': self.form_class,
                                  'form2': form2,
                                  'object_list': self.get_queryset()
                              })

            return HttpResponseRedirect(self.get_success_url())

        if 'single' in request.POST:

            if form1.is_valid():

                session = form1.cleaned_data.get('session')
                programme = form1.cleaned_data.get('programme')
                department = form1.cleaned_data.get('department')

                instance = form1.save(commit=False)
                instance.user_type = UserType.objects.get(user_type="Student")
                instance.password = make_password(PASSWORD)
                instance.save()

                StudentProfile.objects.create(
                    user=instance, department=department, session=session, programme=programme)
                messages.success(request, "Student created successfully!")
            else:

                messages.error(request, form1.errors.as_text())
                return render(request, 'backend/admin/manage_student.html',

                              context={
                                  'form1': form1,
                                  'form2': self.second_form_class,
                                  'object_list': self.get_queryset()
                              })

            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("auth:manage_student")


class UpdateStudentView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "backend/admin/edit_delete_student.html"
    form_class = EditSingleStudentForm
    success_message = 'Updated Successfully!'
    queryset = User.objects.all()

    def get_success_url(self):
        return reverse("auth:manage_student")

    def form_valid(self, form):

        student = StudentProfile.objects.get(user=form.instance)
        student.session = form.cleaned_data.get('session')
        student.department = form.cleaned_data.get('department')
        student.programme = form.cleaned_data.get('programme')
        student.save()
        form = super().form_valid(form)

        return form


class DeleteStudentView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    success_message = 'Deleted Successfully!'
    success_url = reverse_lazy('auth:manage_student')


class ManageOfficeView(LoginRequiredMixin, ListView):
    template_name = "backend/admin/manage_office.html"
    model = User
    form_class = CreateAdministrativeProfileForm
    queryset = AdministrativeProfile.objects.all().order_by('-date_created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form1"] = self.form_class
        return context

    def post(self, request):

        form1 = self.form_class(request.POST, request.FILES)

        if form1.is_valid():

            administrative_office = form1.cleaned_data.get(
                'administrative_office')
            administrative_office_department = form1.cleaned_data.get(
                'administrative_office_department')

            if administrative_office.office_title == 'Department' and administrative_office_department == None:
                form1.add_error('administrative_office_department',
                                'Select administrative_office_department')
                messages.error(
                    request, 'Select administrative office department if office is related to a department')
                return render(request, 'backend/admin/manage_office.html',

                    context={
                        'form1': form1,
                        'object_list': self.get_queryset()
                    }
                )
            signature = form1.cleaned_data.get('signature')

            instance = form1.save(commit=False)
            instance.password = make_password(PASSWORD)
            instance.user_type = UserType.objects.get(user_type="Office")
            instance.save()

            AdministrativeProfile.objects.create(
                user=instance, office=administrative_office, a_departmental_office=administrative_office_department, signature=signature)

            messages.success(request, "Student created successfully!")
        else:

            messages.error(request, form1.errors.as_text())
            return render(request, 'backend/admin/manage_office.html',

                          context={
                              'form1': form1,
                              'object_list': self.get_queryset()
                          })

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("auth:manage_offices")
