# Generated by Django 5.0.6 on 2024-06-07 17:47

import recipes.utils
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0013_temp_recipe_recipe"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe_step",
            name="image",
            field=models.ImageField(null=True, upload_to=recipes.utils.upload_image),
        ),
        migrations.AlterField(
            model_name="temp_step",
            name="image",
            field=models.ImageField(
                null=True, upload_to=recipes.utils.temp_upload_image
            ),
        ),
        migrations.DeleteModel(
            name="Temp",
        ),
    ]
