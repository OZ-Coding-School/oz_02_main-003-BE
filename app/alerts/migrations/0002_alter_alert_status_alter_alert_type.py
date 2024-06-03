# Generated by Django 5.0.6 on 2024-06-02 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alerts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='status',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='alert',
            name='type',
            field=models.PositiveIntegerField(choices=[(1, 'Like'), (2, 'Comment'), (3, 'Bookmark')], default=1),
        ),
    ]