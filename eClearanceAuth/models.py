from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.shortcuts import reverse
import uuid
from datetime import datetime
# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, name, password=None):

        # creates a user with the parameters
        if username is None:
            raise ValueError('Reg. No or File No. is required!')

        if name is None:
            raise ValueError('Full name is required!')

        if password is None:
            raise ValueError('Password is required!')

        user = self.model(
            username=username.upper().strip(),
            name=name.title().strip(),
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, name, password=None):
        # create a superuser with the above parameters

        user = self.create_user(
            username=username,
            name=name,
            password=password,
        )

        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)

        return user


class UserType(models.Model):
    user_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.user_type

    class Meta:
        db_table = 'user type'
        verbose_name_plural = 'user type'


class Department(models.Model):
    dept_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)
    dept_title = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.dept_title

    class Meta:
        db_table = 'Department'
        verbose_name_plural = 'Departments'


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    username = models.CharField(max_length=100, db_index=True,
                                unique=True, verbose_name='reg number', blank=True)

    passport = models.ImageField(
        default='img/user.png', upload_to='uploads/passport/', null=True)

    user_type = models.ForeignKey(
        to="UserType", on_delete=models.CASCADE, blank=True, null=True,)

    name = models.CharField(
        max_length=100, db_index=True, blank=True, null=True)

    date_joined = models.DateTimeField(
        verbose_name='date_joined', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='last_login', auto_now=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'

    REQUIRED_FIELDS = ['name',]

    objects = UserManager()

    def __str__(self):
        return f'{self.username}'

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = 'Users'
        verbose_name_plural = 'Users'


class Session(models.Model):
    session_title = models.CharField(max_length=9, unique=True)
    session_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.session_title

    class Meta:
        db_table = 'Session'
        verbose_name_plural = 'Sessions'


class Programme(models.Model):
    programme_title = models.CharField(max_length=30, unique=True)
    programme_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.programme_title

    class Meta:
        db_table = 'Programme'
        verbose_name_plural = 'Programmes'


class Office(models.Model):
    office_title = models.CharField(max_length=30, unique=True)
    office_description = models.CharField(
        max_length=100, blank=True, null=True)

    def __str__(self):
        return self.office_title

    class Meta:
        db_table = 'Office'
        verbose_name_plural = 'Offices'


class AdministrativeProfile(models.Model):

    profile_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    user = models.OneToOneField(
        to="User", on_delete=models.CASCADE, blank=True)

    office = models.ForeignKey(
        to="Office", on_delete=models.CASCADE, blank=True, null=True)

    a_departmental_office = models.ForeignKey(
        to="Department", on_delete=models.CASCADE, blank=True, null=True)

    signature = models.ImageField(
        upload_to='uploads/signature/', null=True, blank=True)

    date_created = models.DateTimeField(
        verbose_name='date_created', auto_now_add=True)

    def __str__(self):
        return f"{self.user.name}"

    class Meta:
        db_table = 'Administrative Profile'
        verbose_name_plural = 'Administrative Profile'


class StudentProfile(models.Model):
    stud_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    user = models.OneToOneField(
        to="User", on_delete=models.CASCADE, blank=True)
    department = models.ForeignKey(
        to="Department", on_delete=models.CASCADE, blank=True)
    session = models.ForeignKey(
        to="Session", on_delete=models.CASCADE, blank=True)
    programme = models.ForeignKey(
        to="Programme", on_delete=models.CASCADE, blank=True)

    date_joined = models.DateTimeField(
        verbose_name='date_joined', auto_now_add=True)

    def __str__(self):
        return self.user.name

    class Meta:
        db_table = 'Student Profile'
        verbose_name_plural = 'Student Profile'


class StudentClearance(models.Model):

    clearance_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False)

    student = models.OneToOneField(
        to="StudentProfile", on_delete=models.CASCADE, blank=True, null=True)

    hostel_clearance = models.OneToOneField(
        to="HostelClearance", on_delete=models.CASCADE, blank=True, null=True)

    library_clearance = models.OneToOneField(
        to="LibraryClearance", on_delete=models.CASCADE, blank=True, null=True)

    sport_clearance = models.OneToOneField(
        to="SportClearance", on_delete=models.CASCADE, blank=True, null=True)

    internal_audit_clearance = models.OneToOneField(
        to="InternalAuditClearance", on_delete=models.CASCADE, blank=True, null=True)

    departmental_clearance = models.OneToOneField(
        to="DepartmentalClearance", on_delete=models.CASCADE, blank=True, null=True)

    date_applied = models.DateTimeField(auto_now=True)

    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.user.name} : {self.status}"

    class Meta:
        db_table = 'Student Clearance'
        verbose_name_plural = 'Student Clearance'


class LibraryClearance(models.Model):

    number_of_book_owe_departmental = models.IntegerField(
        default=0, blank=True, null=True)
    cost_of_book_owe_departmental = models.FloatField(
        blank=True, null=True, default=0)

    number_of_book_owe_main = models.IntegerField(
        default=0, blank=True, null=True)
    cost_of_book_owe_main = models.FloatField(blank=True, null=True, default=0)

    clearance = models.OneToOneField(
        to="StudentClearance", on_delete=models.CASCADE, blank=True, null=True)

    cleared_by = models.ForeignKey(
        to="AdministrativeProfile", on_delete=models.CASCADE, blank=True, null=True)

    date_cleared = models.DateTimeField(auto_now=True)

    is_cleared = models.BooleanField(default=False)
    is_disapprove = models.BooleanField(default=False)

    def __str__(self):
        return f"Library Clearance Status : {self.is_cleared}"

    class Meta:
        db_table = 'Library Clearance'
        verbose_name_plural = 'Library Clearance'


class SportClearance(models.Model):

    number_sport_items_owed = models.IntegerField(
        default=0, blank=True, null=True)
    cost_of_sport_items_owed = models.FloatField(blank=True, null=True)

    cleared_by = models.ForeignKey(
        to="AdministrativeProfile", on_delete=models.CASCADE, blank=True, null=True)

    clearance = models.OneToOneField(
        to="StudentClearance", on_delete=models.CASCADE, blank=True, null=True)

    date_cleared = models.DateTimeField(auto_now=True)

    is_cleared = models.BooleanField(default=False)
    is_disapprove = models.BooleanField(default=False)

    def __str__(self):
        return f"Sport Clearance Status : {self.is_cleared}"

    class Meta:
        db_table = 'Sport Clearance'
        verbose_name_plural = 'Sport Clearance'


class HostelClearance(models.Model):

    number_of_hostel_items_owed = models.IntegerField(
        default=0, blank=True, null=True)
    cost_of_hostel_items_owed = models.FloatField(blank=True, null=True)

    cleared_by = models.ForeignKey(
        to="AdministrativeProfile", on_delete=models.CASCADE, blank=True, null=True)

    clearance = models.OneToOneField(
        to="StudentClearance", on_delete=models.CASCADE, blank=True, null=True)

    date_cleared = models.DateTimeField(auto_now=True)

    is_cleared = models.BooleanField(default=False)
    is_disapprove = models.BooleanField(default=False)

    def __str__(self):
        return f"Hostel Clearance Status : {self.is_cleared}"

    class Meta:
        db_table = 'Hostel Clearance'
        verbose_name_plural = 'Hostel Clearance'


class InternalAuditClearance(models.Model):

    departmental_clearance_one = models.ImageField(
        upload_to='uploads/clearance/', null=True)
    departmental_clearance_two = models.ImageField(
        upload_to='uploads/clearance/', null=True)

    school_fee_receipt_one = models.ImageField(
        upload_to='uploads/clearance/', null=True)
    school_fee_receipt_two = models.ImageField(
        upload_to='uploads/clearance/', null=True)

    school_id_card = models.ImageField(
        upload_to='uploads/clearance/', null=True)

    remita_one = models.ImageField(upload_to='uploads/clearance/', null=True)
    remita_two = models.ImageField(upload_to='uploads/clearance/', null=True)

    disapproval_reason = models.TextField(blank=True, null=True)
    clearance = models.OneToOneField(
        to="StudentClearance", on_delete=models.CASCADE, blank=True, null=True)

    cleared_by = models.ForeignKey(
        to="AdministrativeProfile", on_delete=models.CASCADE, blank=True, null=True)

    date_cleared = models.DateTimeField(auto_now=True)

    is_cleared = models.BooleanField(default=False)
    is_disapprove = models.BooleanField(default=False)

    def __str__(self):
        return f"Internal Audit Clearance Status : {self.is_cleared}"

    class Meta:
        db_table = 'Internal Audit Clearance'
        verbose_name_plural = 'Internal Audit Clearance'


class DepartmentalClearance(models.Model):

    disapproval_reason = models.TextField(blank=True, null=True)

    cleared_by = models.ForeignKey(
        to="AdministrativeProfile", on_delete=models.CASCADE, blank=True, null=True)

    department = models.ForeignKey(
        to="Department", on_delete=models.CASCADE, blank=True, null=True)

    date_cleared = models.DateTimeField(auto_now=True)

    is_cleared = models.BooleanField(default=False)
    is_disapprove = models.BooleanField(default=False)

    clearance = models.OneToOneField(
        to="StudentClearance", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"Departmental Clearance Status : {self.is_cleared}"

    class Meta:
        db_table = 'Departmental Clearance'
        verbose_name_plural = 'Departmental Clearance'
