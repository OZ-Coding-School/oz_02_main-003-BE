# Generated by Django 5.0.6 on 2024-06-05 15:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0008_alter_recipe_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="main_image",
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name="recipe_step",
            name="image",
            field=models.CharField(default=None, max_length=255, null=True),
        ),
    ]
