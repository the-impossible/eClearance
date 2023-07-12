# Generated by Django 4.2.3 on 2023-07-12 02:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0007_administrativeprofile_office"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="office", options={"verbose_name_plural": "Offices"},
        ),
        migrations.AddField(
            model_name="administrativeprofile",
            name="a_departmental_office",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.department",
            ),
        ),
        migrations.AlterField(
            model_name="administrativeprofile",
            name="signature",
            field=models.ImageField(
                blank=True, null=True, upload_to="uploads/signature/"
            ),
        ),
    ]
