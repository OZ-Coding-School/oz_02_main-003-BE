# Generated by Django 5.0.6 on 2024-06-12 11:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_temp_user_user"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Temp_user",
        ),
    ]
