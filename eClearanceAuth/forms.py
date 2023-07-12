import csv
import io
from django import forms
from eClearanceAuth.models import *

class FileHandler:
    def __init__(self, obj):
        self.csv_obj = obj

    def validate_stud_file(self):
        for col in self.csv_obj:
            existing_users = User.objects.filter(username=col[0])
            if len(col) != 2:
                raise forms.ValidationError('Invalid CSV FILE')
            for row in col:
                if row == '':
                    raise forms.ValidationError('Invalid CSV, Missing DATA!!')
            if existing_users.exists():
                raise forms.ValidationError(
                    f'File contains already registered registration number! {existing_users[0].username}')


class CreateMultipleStudentForm(forms.Form):
    file = forms.FileField(help_text='Select Student CSV file', widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': '.csv'
        }
    ))

    session = forms.ModelChoiceField(queryset=Session.objects.all(), empty_label="(Select Session)", required=True, help_text="Select academic session", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    programme = forms.ModelChoiceField(queryset=Programme.objects.all(), empty_label="(Select Programme)", required=True, help_text="Select student's programme", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="(Select Department)", required=True, help_text="Select student's department", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    def clean_file(self):

        file = io.TextIOWrapper(self.cleaned_data.get('file').file)

        csv_obj = csv.reader(file)

        handler = FileHandler(csv_obj)
        handler.validate_stud_file()

        return file


class CreateSingleStudentForm(forms.ModelForm):

    session = forms.ModelChoiceField(queryset=Session.objects.all(), empty_label="(Select Session)", required=True, help_text="Select academic session", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    programme = forms.ModelChoiceField(queryset=Programme.objects.all(), empty_label="(Select Programme)", required=True, help_text="Select students programme", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="(Select Department)", required=True, help_text="Select student's department", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    username = forms.CharField(help_text='Enter Registration number', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter Registration number',
        }
    ))

    name = forms.CharField(help_text='Enter Full name', widget=forms.TextInput(
        attrs={
            'placeholder': 'Enter Full name',
            'class': 'form-control',
        }
    ))

    passport = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    def clean_username(self):
        username = self.cleaned_data.get('username').upper()
        exists = User.objects.filter(username=username).exists()

        if exists:
            raise forms.ValidationError("Account already exist!")

        return username


    class Meta:
        model = User
        fields = ('username', 'name', 'passport')


class EditSingleStudentForm(CreateSingleStudentForm):

    def __init__(self, *args, **kwargs):
        super(CreateSingleStudentForm, self).__init__(*args, **kwargs)
        student_profile = StudentProfile.objects.get(user=kwargs['instance'])
        student_department = Department.objects.get(dept_title=student_profile.department)
        student_programme = Programme.objects.get(programme_title=student_profile.programme)
        student_session = Session.objects.get(session_title=student_profile.session)
        self.fields['session'].initial = student_session
        self.fields['programme'].initial = student_programme
        self.fields['department'].initial = student_department

    session = forms.ModelChoiceField(queryset=Session.objects.all(), empty_label="(Select Session)", required=True, help_text="Select academic session", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    programme = forms.ModelChoiceField(queryset=Programme.objects.all(), empty_label="(Select Programme)", required=True, help_text="Select students programme", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="(Select Department)", required=True, help_text="Select student's department", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    def clean_username(self):
        username = self.cleaned_data.get('username').upper()
        check = User.objects.filter(username=username)

        if self.instance:
            check = check.exclude(pk=self.instance.pk)

        if check.exists():
            raise forms.ValidationError("Username already exist!")

        return username


    class Meta:
        model = User
        fields = ('username', 'name', 'passport', 'session', 'programme', 'department')


"""
class AdministrativeProfile(models.Model):

   profile_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    user = models.OneToOneField(
        to="User", on_delete=models.CASCADE, blank=True)

    office = models.ForeignKey(
        to="Office", on_delete=models.CASCADE, blank=True, null=True)

    a_departmental_office = models.ForeignKey(to="Department", on_delete=models.CASCADE, blank=True, null=True)

    signature = models.ImageField(upload_to='uploads/signature/', null=True, blank=True)
"""

class CreateAdministrativeProfileForm(forms.ModelForm):

    username = forms.CharField(help_text='Enter File number', widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter File number',
        }
    ))

    name = forms.CharField(help_text='Enter Full name', widget=forms.TextInput(
        attrs={
            'placeholder': 'Enter Full name',
            'class': 'form-control',
        }
    ))

    passport = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    signature = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    administrative_office = forms.ModelChoiceField(queryset=Office.objects.all(), empty_label="(Select administrative office)", required=True, help_text="Select administrative office", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))

    administrative_office_department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="(Select administrative office department )", required=False, help_text="if administrative office is related to a department then select department otherwise skip", widget=forms.Select(
        attrs={
            'class': 'form-control',
        }
    ))


    class Meta:
        model = User
        fields = ('username', 'name', 'passport')
