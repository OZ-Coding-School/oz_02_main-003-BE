# Generated by Django 5.0.6 on 2024-05-31 14:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="unit",
            old_name="code",
            new_name="id",
        ),
        migrations.RemoveField(
            model_name="recipe_ingredient",
            name="code",
        ),
    ]
