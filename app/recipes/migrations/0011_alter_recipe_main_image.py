# Generated by Django 5.0.6 on 2024-06-05 16:45

import recipes.utils
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0010_alter_recipe_main_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="main_image",
            field=models.ImageField(upload_to=recipes.utils.upload_image),
        ),
    ]
