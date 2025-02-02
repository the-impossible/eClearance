# Generated by Django 4.2.3 on 2023-07-13 03:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0012_departmentalclearance_student_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="departmentalclearance",
            old_name="student",
            new_name="clearance",
        ),
        migrations.RenameField(
            model_name="hostelclearance", old_name="student", new_name="clearance",
        ),
        migrations.RenameField(
            model_name="internalauditclearance",
            old_name="student",
            new_name="clearance",
        ),
        migrations.RenameField(
            model_name="libraryclearance", old_name="student", new_name="clearance",
        ),
        migrations.RenameField(
            model_name="sportclearance", old_name="student", new_name="clearance",
        ),
    ]
