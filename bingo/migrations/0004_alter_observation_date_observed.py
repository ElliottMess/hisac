# Generated by Django 5.0 on 2023-12-18 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bingo', '0003_remove_creature_name_creature_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='observation',
            name='date_observed',
            field=models.DateField(),
        ),
    ]
