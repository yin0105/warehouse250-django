# Generated by Django 3.2.4 on 2021-06-21 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0006_auto_20210616_2211'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='products_limit',
            field=models.IntegerField(default=0),
        ),
    ]