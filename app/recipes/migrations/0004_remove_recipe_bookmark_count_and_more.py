# Generated by Django 5.0.6 on 2024-06-03 16:46

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0003_rename_image1_recipe_image_1_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recipe",
            name="bookmark_count",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="comment_count",
        ),
        migrations.RemoveField(
            model_name="recipe",
            name="like_count",
        ),
    ]
