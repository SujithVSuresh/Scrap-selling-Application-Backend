# Generated by Django 3.2.18 on 2023-04-11 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_auto_20230406_1708'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='price',
        ),
    ]