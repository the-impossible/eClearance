# Generated by Django 4.2.3 on 2023-07-14 03:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "eClearanceAuth",
            "0014_alter_libraryclearance_cost_of_book_owe_departmental_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(model_name="sportclearance", name="sport_items_owed",),
    ]
