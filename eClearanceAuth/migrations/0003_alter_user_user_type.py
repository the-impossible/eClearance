# Generated by Django 4.2.3 on 2023-07-10 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eClearanceAuth", "0002_alter_user_user_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="user_type",
            field=models.ForeignKey(
                blank=True,
                default=(),
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="eClearanceAuth.usertype",
            ),
        ),
    ]
