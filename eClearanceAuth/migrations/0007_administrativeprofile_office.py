# Generated by Django 4.2.3 on 2023-07-11 20:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0006_office"),
    ]

    operations = [
        migrations.AddField(
            model_name="administrativeprofile",
            name="office",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.office",
            ),
        ),
    ]
