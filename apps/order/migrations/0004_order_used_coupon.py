# Generated by Django 3.2.4 on 2021-06-23 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20210607_1914'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='used_coupon',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
