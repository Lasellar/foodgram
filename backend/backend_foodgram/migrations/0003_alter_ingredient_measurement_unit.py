# Generated by Django 5.1.4 on 2024-12-18 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend_foodgram', '0002_remove_recipe_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=4, verbose_name='Мера измерения'),
        ),
    ]
