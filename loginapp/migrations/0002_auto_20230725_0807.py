# Generated by Django 3.2 on 2023-07-25 00:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Apage',
        ),
        migrations.DeleteModel(
            name='Bpage',
        ),
        migrations.AlterField(
            model_name='test',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 25, 8, 7, 22, 308101), verbose_name='時間'),
        ),
    ]
