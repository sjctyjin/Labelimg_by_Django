# Generated by Django 3.2.16 on 2023-02-03 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loginapp', '0002_test_dame'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='test',
            name='dame',
        ),
    ]
