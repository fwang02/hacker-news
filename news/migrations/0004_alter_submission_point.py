# Generated by Django 5.1.2 on 2024-11-10 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_submission_point'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='point',
            field=models.IntegerField(default=1),
        ),
    ]
