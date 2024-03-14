from django.shortcuts import render, redirect, reverse, get_object_or_404
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.user_type.user_type == "Admin":
            context["student"] = User.objects.filter(
                user_type=UserType.objects.get(user_type='Student')).count()
            context["office"] = User.objects.filter(
                user_type=UserType.objects.get(user_type='Office')).count()
            context["completed"] = DepartmentalClearance.objects.filter(
                is_cleared=True).count()
            context["applied"] = StudentClearance.objects.all().count()
        elif self.request.user.user_type.user_type == "Office":
            try:
                profile = AdministrativeProfile.objects.get(
                    user=User.objects.get(username=self.request.user))
                office_type = profile.office.office_title

                if office_type == 'Library':
                    context["approve"] = LibraryClearance.objects.filter(
                        is_cleared=True).count()
                    context["disapprove"] = LibraryClearance.objects.filter(
                        is_disapprove=True).count()
                    context["applied"] = context["approve"] + \
                        context["disapprove"]
                elif office_type == 'Hostel':
                    context["approve"] = HostelClearance.objects.filter(
                        is_cleared=True).count()
                    context["disapprove"] = HostelClearance.objects.filter(
                        is_disapprove=True).count()
                    context["applied"] = context["approve"] + \
                        context["disapprove"]
                elif office_type == 'Sport':
                    context["approve"] = SportClearance.objects.filter(
                        is_cleared=True).count()
                    context["disapprove"] = SportClearance.objects.filter(
                        is_disapprove=True).count()
                    context["applied"] = context["approve"] + \
                        context["disapprove"]
                elif office_type == 'Internal Audit':
                    context["approve"] = InternalAuditClearance.objects.filter(
                        is_cleared=True).count()
                    context["disapprove"] = InternalAuditClearance.objects.filter(
                        is_disapprove=True).count()
                    context["applied"] = context["approve"] + \
                        context["disapprove"]
                elif office_type == 'Department':

                    department = AdministrativeProfile.objects.get(
                        user=self.request.user).a_departmental_office
                    context["approve"] = DepartmentalClearance.objects.filter(department=department,
                                                                              is_cleared=True).count()
                    context["disapprove"] = DepartmentalClearance.objects.filter(department=department,
                                                                                 is_disapprove=True).count()
                    context["applied"] = context["approve"] + \
                        context["disapprove"]

            except AdministrativeProfile.DoesNotExist:
                return None

            except User.DoesNotExist:
                return None

        elif self.request.user.user_type.user_type == "Student":
            student_clearance = StudentClearance.objects.filter(
                student=StudentProfile.objects.get(user=self.request.user))

            if student_clearance:
                if student_clearance[0].departmental_clearance.is_cleared:
                    context["status"] = "Completed"
                else:
                    context["status"] = "In progress"

            else:
                context["status"] = "Has not applied"

        return context


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
            if administrative_office.office_title != 'Department' and administrative_office_department != None:
                administrative_office_department = None

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


class UpdateAdministrativeOfficeView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "backend/admin/edit_delete_office.html"
    form_class = EditAdministrativeProfileForm
    success_message = 'Updated Successfully!'
    queryset = User.objects.all()

    def get_success_url(self):
        return reverse("auth:manage_offices")

    def form_valid(self, form):

        admin = AdministrativeProfile.objects.get(user=form.instance)
        if not form.cleaned_data.get('signature') == None:
            admin.signature = form.cleaned_data.get('signature')

        administrative_office = form.cleaned_data.get(
            'administrative_office')
        administrative_office_department = form.cleaned_data.get(
            'administrative_office_department')

        if administrative_office.office_title == 'Department' and administrative_office_department == None:
            form.add_error('administrative_office_department',
                           'Select administrative_office_department')
            messages.error(
                self.request, 'Select administrative office department if office is related to a department')
            return render(self.request, 'backend/admin/edit_delete_office.html',

                          context={
                              'form': form,
                              'object': self.get_object()
                          }
                          )

        if administrative_office.office_title != 'Department' and administrative_office_department != None:
            admin.a_departmental_office = None
        else:
            admin.a_departmental_office = administrative_office_department

        admin.office = administrative_office
        admin.save()
        form = super().form_valid(form)

        return form


class DeleteAdministrativeOfficeView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = User
    success_message = 'Deleted Successfully!'
    success_url = reverse_lazy('auth:manage_offices')


class ApplyClearanceView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    form_class = ClearanceForm
    template_name = "backend/users/apply_clearance.html"
    success_message = "Application successful you can now track status"

    def has_applied(self):
        student_clearance = StudentClearance.objects.filter(
            student=StudentProfile.objects.get(user=self.request.user))
        if student_clearance:
            self.form_class = ClearanceForm(
                instance=student_clearance[0].internal_audit_clearance)
            return [True, student_clearance[0]]
        return [False, None]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class
        context["clearance"] = self.has_applied()[1]
        context["has_applied"] = self.has_applied()[0]
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if 're-upload' in request.POST:

            student = StudentProfile.objects.get(user=self.request.user)
            clearance = StudentClearance.objects.get(student=student)

            form = self.form_class(
                request.POST, request.FILES, instance=clearance.internal_audit_clearance)

        if form.is_valid():
            instance = form.save(commit=False)
            student = StudentProfile.objects.get(user=self.request.user)

            passport = str(student.user.passport).split("/")[-1].split(".")[0]

            if passport == 'user':
                messages.error(self.request, "You have to update your profile")
                return render(self.request, self.template_name, context={'form': form, 'has_applied': self.has_applied()[0]})

            if 're-upload' in request.POST:

                instance.is_disapprove = False
                instance.disapproval_reason = ""
                instance.save()

                messages.success(self.request, self.success_message)

                return HttpResponseRedirect(self.get_success_url())

            else:
                print("NO 3")

                clearance = StudentClearance.objects.create(student=student)

                library = LibraryClearance.objects.create(clearance=clearance)
                hostel = HostelClearance.objects.create(clearance=clearance)
                sport = SportClearance.objects.create(clearance=clearance)
                department = DepartmentalClearance.objects.create(
                    clearance=clearance, department=student.department)
                instance.clearance = clearance

                instance.save()

                clearance.library_clearance = library
                clearance.hostel_clearance = hostel
                clearance.sport_clearance = sport
                clearance.internal_audit_clearance = instance
                clearance.departmental_clearance = department
                clearance.save()

                messages.success(self.request, self.success_message)

                return HttpResponseRedirect(self.get_success_url())
        else:
            messages.error(self.request, form.errors.as_text())

            return render(self.request, self.template_name, context={'form': form, 'has_applied': self.has_applied()[0]})

    def get_success_url(self):
        return reverse("auth:manage_clearance")


class ClearanceApplicationView(LoginRequiredMixin, SuccessMessageMixin, ListView):
    template_name = "backend/office/manage_office.html"
    model = None
    queryset = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form
        context["office"] = self.office
        return context

    def get_office_type(self):
        try:
            profile = AdministrativeProfile.objects.get(
                user=User.objects.get(username=self.request.user))
            office_type = profile.office.office_title
            return office_type
        except AdministrativeProfile.DoesNotExist:
            return None

        except User.DoesNotExist:
            return None

    def get_queryset(self):

        office_type = self.get_office_type()
        self.office = office_type

        if office_type != None:

            if office_type == 'Library':
                # get library student

                self.form = LibraryClearanceForm

                # Retrieve library clearances that are not cleared and not disapproved
                queryset = LibraryClearance.objects.filter(
                    is_cleared=False, is_disapprove=False).order_by('-date_cleared')

                # Filter by student clearance with hostel clearance cleared
                queryset = queryset.filter(clearance__hostel_clearance__is_cleared=False, clearance__sport_clearance__is_cleared=False,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Hostel':

                self.form = HostelClearanceForm

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = HostelClearance.objects.filter(
                    is_cleared=False, is_disapprove=False).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__sport_clearance__is_cleared=False,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Sport':

                self.form = SportClearanceForm

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = SportClearance.objects.filter(
                    is_cleared=False, is_disapprove=False).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Internal Audit':

                self.form = InternalClearanceForm

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = InternalAuditClearance.objects.filter(
                    is_cleared=False, is_disapprove=False).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__sport_clearance__is_cleared=True, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Department':

                self.form = DepartmentClearanceForm

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = DepartmentalClearance.objects.filter(
                    is_cleared=False, is_disapprove=False).order_by('-date_cleared')

                profile = AdministrativeProfile.objects.get(
                    user=User.objects.get(username=self.request.user))

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__sport_clearance__is_cleared=True, clearance__internal_audit_clearance__is_cleared=True, department=profile.a_departmental_office)
                return queryset

        else:
            # Failed in getting office type
            pass

        return None

    def get_success_url(self):
        return reverse("auth:clearance_application")

    def post(self, request, *args, **kwargs):

        office_type = self.get_office_type()

        if office_type != None:

            if office_type == 'Library':
                # get library student
                if 'approve' in request.POST:
                    clearance_id = request.POST['clearance_id']
                    library_clearance = LibraryClearance.objects.get(
                        pk=clearance_id)
                    library_clearance.is_cleared = True
                    library_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    library_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

                if 'disapprove' in request.POST:
                    form = LibraryClearanceForm(request.POST)

                    if form.is_valid():

                        clearance_id = request.POST['clearance_id']

                        library_clearance = LibraryClearance.objects.get(
                            pk=clearance_id)
                        library_clearance.is_disapprove = True

                        library_clearance.number_of_book_owe_departmental = form.cleaned_data.get(
                            'number_of_book_owe_departmental')
                        library_clearance.cost_of_book_owe_departmental = form.cleaned_data.get(
                            'cost_of_book_owe_departmental')

                        library_clearance.number_of_book_owe_main = form.cleaned_data.get(
                            'number_of_book_owe_main')
                        library_clearance.cost_of_book_owe_main = form.cleaned_data.get(
                            'cost_of_book_owe_main')

                        library_clearance.cleared_by = AdministrativeProfile.objects.get(
                            user=self.request.user)

                        library_clearance.save()
                        messages.success(
                            request, "Student clearance has been disapproved with a reason")

                        return HttpResponseRedirect(self.get_success_url())

                    messages.error(request, form.errors.as_text())
                    return render(request, self.template_name, {'form': form, 'object_list': self.get_queryset()})

            if office_type == 'Hostel':
                # get library student
                clearance_id = request.POST['clearance_id']
                hostel_clearance = HostelClearance.objects.get(pk=clearance_id)

                if 'approve' in request.POST:
                    hostel_clearance.is_cleared = True
                    hostel_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    hostel_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

                if 'disapprove' in request.POST:
                    form = HostelClearanceForm(request.POST)

                    if form.is_valid():

                        hostel_clearance.is_disapprove = True

                        hostel_clearance.number_of_hostel_items_owed = form.cleaned_data.get(
                            'number_of_hostel_items_owed')
                        hostel_clearance.cost_of_hostel_items_owed = form.cleaned_data.get(
                            'cost_of_hostel_items_owed')

                        hostel_clearance.cleared_by = AdministrativeProfile.objects.get(
                            user=self.request.user)

                        hostel_clearance.save()
                        messages.success(
                            request, "Student clearance has been disapproved with a reason")

                        return HttpResponseRedirect(self.get_success_url())

                    messages.error(request, form.errors.as_text())
                    return render(request, self.template_name, {'form': form, 'object_list': self.get_queryset()})

            if office_type == 'Sport':
                # get library student
                clearance_id = request.POST['clearance_id']
                sport_clearance = SportClearance.objects.get(pk=clearance_id)

                if 'approve' in request.POST:
                    sport_clearance.is_cleared = True
                    sport_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    sport_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

                if 'disapprove' in request.POST:
                    form = SportClearanceForm(request.POST)

                    if form.is_valid():

                        sport_clearance.is_disapprove = True

                        sport_clearance.number_sport_items_owed = form.cleaned_data.get(
                            'number_sport_items_owed')
                        sport_clearance.cost_of_sport_items_owed = form.cleaned_data.get(
                            'cost_of_sport_items_owed')

                        sport_clearance.cleared_by = AdministrativeProfile.objects.get(
                            user=self.request.user)

                        sport_clearance.save()
                        messages.success(
                            request, "Student clearance has been disapproved with a reason")

                        return HttpResponseRedirect(self.get_success_url())

                    messages.error(request, form.errors.as_text())
                    return render(request, self.template_name, {'form': form, 'object_list': self.get_queryset()})

            if office_type == 'Internal Audit':
                # get internal audit student
                clearance_id = request.POST['clearance_id']
                internal_clearance = InternalAuditClearance.objects.get(
                    pk=clearance_id)

                if 'approve' in request.POST:
                    internal_clearance.is_cleared = True
                    internal_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    internal_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

                if 'disapprove' in request.POST:
                    form = InternalClearanceForm(request.POST)

                    if form.is_valid():

                        internal_clearance.is_disapprove = True

                        internal_clearance.disapproval_reason = form.cleaned_data.get(
                            'disapproval_reason')

                        internal_clearance.cleared_by = AdministrativeProfile.objects.get(
                            user=self.request.user)

                        internal_clearance.save()
                        messages.success(
                            request, "Student clearance has been disapproved with a reason")

                        return HttpResponseRedirect(self.get_success_url())

                    messages.error(request, form.errors.as_text())
                    return render(request, self.template_name, {'form': form, 'object_list': self.get_queryset()})

            if office_type == 'Department':
                # get internal audit student
                clearance_id = request.POST['clearance_id']
                department_clearance = DepartmentalClearance.objects.get(
                    pk=clearance_id)

                if 'approve' in request.POST:
                    department_clearance.is_cleared = True
                    department_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    department_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

                if 'disapprove' in request.POST:
                    form = DepartmentClearanceForm(request.POST)

                    if form.is_valid():

                        department_clearance.is_disapprove = True

                        department_clearance.disapproval_reason = form.cleaned_data.get(
                            'disapproval_reason')

                        department_clearance.cleared_by = AdministrativeProfile.objects.get(
                            user=self.request.user)

                        department_clearance.save()
                        messages.success(
                            request, "Student clearance has been disapproved with a reason")

                        return HttpResponseRedirect(self.get_success_url())

                    messages.error(request, form.errors.as_text())
                    return render(request, self.template_name, {'form': form, 'object_list': self.get_queryset()})

        else:
            # Failed in getting office type
            pass


class DisapprovedApplicationView(LoginRequiredMixin, ListView):
    template_name = "backend/office/disapproved.html"

    def get_office_type(self):
        try:
            profile = AdministrativeProfile.objects.get(
                user=User.objects.get(username=self.request.user))
            office_type = profile.office.office_title
            return office_type
        except AdministrativeProfile.DoesNotExist:
            return None

        except User.DoesNotExist:
            return None

    def get_success_url(self):
        return reverse("auth:disapproved_application")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["office"] = self.office
        return context

    def get_queryset(self):

        office_type = self.get_office_type()
        self.office = office_type

        if office_type != None:
            if office_type == 'Library':

                # Retrieve library clearances that are disapproved
                queryset = LibraryClearance.objects.filter(
                    is_cleared=False, is_disapprove=True).order_by('-date_cleared')

                # Filter by student clearance with hostel clearance cleared
                queryset = queryset.filter(clearance__hostel_clearance__is_cleared=False, clearance__sport_clearance__is_cleared=False,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Hostel':

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = HostelClearance.objects.filter(
                    is_cleared=False, is_disapprove=True).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__sport_clearance__is_cleared=False,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Sport':

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = SportClearance.objects.filter(
                    is_cleared=False, is_disapprove=True).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__internal_audit_clearance__is_cleared=False, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Internal Audit':

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = InternalAuditClearance.objects.filter(
                    is_cleared=False, is_disapprove=True).order_by('-date_cleared')

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__sport_clearance__is_cleared=True, clearance__departmental_clearance__is_cleared=False)
                return queryset

            elif office_type == 'Department':

                # Retrieve hostel clearances that are not cleared and not disapproved
                queryset = DepartmentalClearance.objects.filter(
                    is_cleared=False, is_disapprove=True).order_by('-date_cleared')

                profile = AdministrativeProfile.objects.get(
                    user=User.objects.get(username=self.request.user))

                # Filter by student clearance with library clearance cleared
                queryset = queryset.filter(clearance__library_clearance__is_cleared=True, clearance__hostel_clearance__is_cleared=True,
                                           clearance__sport_clearance__is_cleared=True, clearance__internal_audit_clearance__is_cleared=True, department=profile.a_departmental_office)
                return queryset

        else:

            pass

    def post(self, request, *args, **kwargs):

        office_type = self.get_office_type()

        if office_type != None:

            if office_type == 'Library':
                # get library student
                if 'approve' in request.POST:
                    clearance_id = request.POST['clearance_id']
                    library_clearance = LibraryClearance.objects.get(
                        pk=clearance_id)

                    library_clearance.is_cleared = True
                    library_clearance.is_disapprove = False
                    library_clearance.number_of_book_owe_departmental = None
                    library_clearance.cost_of_book_owe_departmental = None
                    library_clearance.number_of_book_owe_main = None
                    library_clearance.cost_of_book_owe_main = None

                    library_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    library_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

            if office_type == 'Hostel':
                # get library student
                clearance_id = request.POST['clearance_id']
                hostel_clearance = HostelClearance.objects.get(pk=clearance_id)

                if 'approve' in request.POST:
                    hostel_clearance.is_cleared = True
                    hostel_clearance.is_disapprove = False
                    hostel_clearance.number_of_hostel_items_owed = None
                    hostel_clearance.cost_of_hostel_items_owed = None

                    hostel_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    hostel_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

            if office_type == 'Sport':
                # get library student
                clearance_id = request.POST['clearance_id']
                sport_clearance = SportClearance.objects.get(pk=clearance_id)

                if 'approve' in request.POST:
                    sport_clearance.is_cleared = True
                    sport_clearance.is_disapprove = False
                    sport_clearance.number_sport_items_owed = None
                    sport_clearance.cost_of_sport_items_owed = None

                    sport_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    sport_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

            if office_type == 'Internal Audit':
                # get internal audit student
                clearance_id = request.POST['clearance_id']
                internal_clearance = InternalAuditClearance.objects.get(
                    pk=clearance_id)

                if 'approve' in request.POST:
                    internal_clearance.is_cleared = True
                    internal_clearance.is_disapprove = False
                    internal_clearance.disapproval_reason = None
                    internal_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    internal_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

            if office_type == 'Department':
                # get internal audit student
                clearance_id = request.POST['clearance_id']
                department_clearance = DepartmentalClearance.objects.get(
                    pk=clearance_id)

                if 'approve' in request.POST:
                    department_clearance.is_cleared = True
                    department_clearance.is_disapprove = False
                    department_clearance.disapproval_reason = None
                    department_clearance.cleared_by = AdministrativeProfile.objects.get(
                        user=self.request.user)
                    messages.success(
                        request, "Student clearance has been approved")
                    department_clearance.save()

                    return HttpResponseRedirect(self.get_success_url())

        else:
            # Failed in getting office type
            pass


class UpdateStudentProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = "backend/users/update_profile.html"
    form_class = UpdateSingleStudentForm
    success_message = 'Updated Successfully!'
    queryset = User.objects.all()

    def get_success_url(self):
        return reverse("auth:update_student_profile", kwargs={'pk': self.object.pk})

    def get_object(self, queryset=None):
        user = super().get_object(queryset=queryset)
        try:
            student_profile = StudentProfile.objects.get(user=user)
            return student_profile
        except StudentProfile.DoesNotExist:
            return user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student_profile'] = self.object
        return context


class ChangePassword(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):

        password0 = request.POST.get('password0')
        password = request.POST.get('password1')
        password1 = request.POST.get('password2')

        if (password != password1):
            messages.error(
                request, 'New password and confirm password does not match!')
            return redirect('auth:update_student_profile', self.kwargs['pk'])

        if (len(password1) < 6):
            messages.error(
                request, 'password too short! should not be less than 6 characters')
            return redirect('auth:update_student_profile', self.kwargs['pk'])

        user = User.objects.get(pk=self.kwargs['pk'])

        if not user.check_password(password0):
            messages.error(request, 'Old password incorrect!')
            return redirect('auth:update_student_profile', self.kwargs['pk'])

        user.set_password(password)
        user.save()

        messages.success(
            request, 'Password reset successful, you can now login!!')
        return redirect('auth:login')


class PrintClearanceView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    form_class = ClearanceForm
    template_name = "backend/users/print_clearance.html"

    def get(self, request, *args, **kwargs):
        student_clearance = StudentClearance.objects.filter(
                student=StudentProfile.objects.get(user=self.request.user))

        if student_clearance[0].departmental_clearance.is_cleared:
            return self.render_to_response(self.get_context_data())
        else:
            messages.error(
                self.request, "You are not yet cleared!!")
            return redirect('auth:dashboard')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student_profile = StudentProfile.objects.get(user=self.request.user)
        context['student_profile'] = student_profile

        library = AdministrativeProfile.objects.filter(
            office=Office.objects.get(office_title='Library'))[0]
        hostel = AdministrativeProfile.objects.filter(
            office=Office.objects.get(office_title='Hostel'))[0]
        sport = AdministrativeProfile.objects.filter(
            office=Office.objects.get(office_title='Sport'))[0]
        audit = AdministrativeProfile.objects.filter(
            office=Office.objects.get(office_title='Internal Audit'))[0]
        department = AdministrativeProfile.objects.filter(
            a_departmental_office=student_profile.department)[0]
        print(library)
        context['library'] = library
        context['hostel'] = hostel
        context['sport'] = sport
        context['audit'] = audit
        context['department'] = department
        return context
