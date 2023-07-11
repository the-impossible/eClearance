# Generated by Django 4.2.3 on 2023-07-11 05:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0004_alter_user_user_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="studentprofile",
            name="date_joined",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="date_joined",
            ),
            preserve_default=False,
        ),
    ]
