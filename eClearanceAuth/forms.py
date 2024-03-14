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
        student_department = Department.objects.get(
            dept_title=student_profile.department)
        student_programme = Programme.objects.get(
            programme_title=student_profile.programme)
        student_session = Session.objects.get(
            session_title=student_profile.session)
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
        fields = ('username', 'name', 'passport',
                  'session', 'programme', 'department')


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

    signature = forms.ImageField(widget=forms.FileInput(
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


class EditAdministrativeProfileForm(CreateAdministrativeProfileForm):

    def __init__(self, *args, **kwargs):
        super(EditAdministrativeProfileForm, self).__init__(*args, **kwargs)
        administrative_profile = AdministrativeProfile.objects.get(
            user=kwargs['instance'])
        administrative_office = Office.objects.get(
            office_title=administrative_profile.office)
        try:
            administrative_office_department = Department.objects.get(
                dept_title=administrative_profile.a_departmental_office)
            self.fields['administrative_office_department'].initial = administrative_office_department
        except Department.DoesNotExist:
            pass
        self.fields['administrative_office'].initial = administrative_office

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
        fields = ('username', 'name', 'passport')


class ClearanceForm(forms.ModelForm):

    departmental_clearance_one = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    departmental_clearance_two = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    school_fee_receipt_one = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    school_fee_receipt_two = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    school_id_card = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    remita_one = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    remita_two = forms.ImageField(widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))

    class Meta:
        model = InternalAuditClearance
        fields = ('departmental_clearance_one', 'departmental_clearance_two', 'school_fee_receipt_one',
                  'school_fee_receipt_two', 'school_id_card', 'remita_one', 'remita_two')


class LibraryClearanceForm(forms.ModelForm):

    number_of_book_owe_departmental = forms.IntegerField(required=False, help_text='Enter numbers of books owed at departmental level', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter numbers of books',
        }
    ))

    cost_of_book_owe_departmental = forms.FloatField(required=False, help_text='Enter cost of books owed at departmental level', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter cost of books',
        }
    ))

    number_of_book_owe_main = forms.IntegerField(required=False, help_text='Enter numbers of books owed at main library', widget=forms.NumberInput(
        attrs={
            'placeholder': 'Enter numbers of books',
            'class': 'form-control',
        }
    ))

    cost_of_book_owe_main = forms.FloatField(required=False, help_text='Enter cost of books owed at main library', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter cost of books',
        }
    ))

    def clean(self):

        cleaned_data = super().clean()
        book_dept = cleaned_data.get('number_of_book_owe_departmental')
        cost_dept = cleaned_data.get('cost_of_book_owe_departmental')
        book_main = cleaned_data.get('number_of_book_owe_main')
        cost_main = cleaned_data.get('cost_of_book_owe_main')

        if not book_dept and not cost_dept and not book_main and not cost_main:
            raise forms.ValidationError("Reason must be provided")

        if book_dept and not cost_dept:
            raise forms.ValidationError("enter cost of book owed at departmental library")

        if cost_dept and not book_dept:
            raise forms.ValidationError("enter number of books owed at departmental library")

        if book_main and not cost_main:
            raise forms.ValidationError("enter cost of book owed at owed at main library")

        if cost_main and not book_main:
            raise forms.ValidationError("enter number of books owed at owed at main library")

        return cleaned_data


    class Meta:
        model = LibraryClearance
        fields = ('number_of_book_owe_departmental', 'cost_of_book_owe_departmental',
                  'number_of_book_owe_main', 'cost_of_book_owe_main')

class HostelClearanceForm(forms.ModelForm):

    number_of_hostel_items_owed = forms.IntegerField(help_text='Enter numbers of hostel items owed', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter numbers of hostel items',
        }
    ))

    cost_of_hostel_items_owed = forms.FloatField(help_text='Enter cost of hostel items owed', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of hostel items',
        }
    ))

    def clean(self):

        cleaned_data = super().clean()
        item_hostel = cleaned_data.get('number_of_hostel_items_owed')
        cost_hostel = cleaned_data.get('cost_of_hostel_items_owed')

        if not item_hostel and not cost_hostel:
            raise forms.ValidationError("Reason must be provided")

        return cleaned_data


    class Meta:
        model = HostelClearance
        fields = ('number_of_hostel_items_owed', 'cost_of_hostel_items_owed')

class SportClearanceForm(forms.ModelForm):

    number_sport_items_owed = forms.IntegerField(help_text='Enter numbers of sport items owed', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter numbers of sport items',
        }
    ))

    cost_of_sport_items_owed = forms.FloatField(help_text='Enter cost of sport items owed', widget=forms.NumberInput(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter number of sport items',
        }
    ))

    def clean(self):

        cleaned_data = super().clean()
        item_sport = cleaned_data.get('number_sport_items_owed')
        cost_sport = cleaned_data.get('cost_of_sport_items_owed')

        if not item_sport and not cost_sport:
            raise forms.ValidationError("Reason must be provided")

        return cleaned_data


    class Meta:
        model = SportClearance
        fields = ('number_sport_items_owed', 'cost_of_sport_items_owed')

class InternalClearanceForm(forms.ModelForm):

    disapproval_reason = forms.CharField(help_text='Enter reason for disapproval', widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter reason for disapproval',
        }
    ))

    def clean(self):

        cleaned_data = super().clean()
        disapproval_reason = cleaned_data.get('disapproval_reason')

        if not disapproval_reason:
            raise forms.ValidationError("Reason must be provided")

        return cleaned_data


    class Meta:
        model = InternalAuditClearance
        fields = ('disapproval_reason',)

class DepartmentClearanceForm(forms.ModelForm):

    disapproval_reason = forms.CharField(help_text='Enter reason for disapproval', widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'placeholder': 'Enter reason for disapproval',
        }
    ))

    def clean(self):

        cleaned_data = super().clean()
        disapproval_reason = cleaned_data.get('disapproval_reason')

        if not disapproval_reason:
            raise forms.ValidationError("Reason must be provided")

        return cleaned_data


    class Meta:
        model = DepartmentalClearance
        fields = ('disapproval_reason',)

class UpdateSingleStudentForm(forms.ModelForm):


    passport = forms.ImageField(required=True, widget=forms.FileInput(
        attrs={
            'class': 'form-control',
            'type': 'file',
            'accept': 'image/png, image/jpeg'
        }
    ))


    class Meta:
        model = User
        fields = ('passport',)

