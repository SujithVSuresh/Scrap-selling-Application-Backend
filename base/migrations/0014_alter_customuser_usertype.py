# Generated by Django 3.2.18 on 2023-04-19 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_remove_orderitem_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='userType',
            field=models.CharField(choices=[('ScraperAdmin', 'ScraperAdmin'), ('ScraperStaff', 'ScraperStaff'), ('ScrapSeller', 'ScrapSeller'), ('Admin', 'Admin')], max_length=100, null=True),
        ),
    ]
