# Generated by Django 4.2.3 on 2023-07-12 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0009_administrativeprofile_date_created"),
    ]

    operations = [
        migrations.AddField(
            model_name="departmentalclearance",
            name="cleared_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.administrativeprofile",
            ),
        ),
        migrations.AddField(
            model_name="departmentalclearance",
            name="date_cleared",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="hostelclearance",
            name="cleared_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.administrativeprofile",
            ),
        ),
        migrations.AddField(
            model_name="hostelclearance",
            name="date_cleared",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="internalauditclearance",
            name="cleared_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.administrativeprofile",
            ),
        ),
        migrations.AddField(
            model_name="internalauditclearance",
            name="date_cleared",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="libraryclearance",
            name="cleared_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.administrativeprofile",
            ),
        ),
        migrations.AddField(
            model_name="libraryclearance",
            name="date_cleared",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="sportclearance",
            name="cleared_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.administrativeprofile",
            ),
        ),
        migrations.AddField(
            model_name="sportclearance",
            name="date_cleared",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="departmental_clearance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.departmentalclearance",
            ),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="hostel_clearance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.hostelclearance",
            ),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="internal_audit_clearance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.internalauditclearance",
            ),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="library_clearance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.libraryclearance",
            ),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="sport_clearance",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.sportclearance",
            ),
        ),
        migrations.AlterField(
            model_name="studentclearance",
            name="student",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.studentprofile",
            ),
        ),
    ]
