# Generated by Django 3.2.5 on 2021-07-15 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0003_auto_20210715_0629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receiver',
            name='bday',
            field=models.DateField(blank=True, null=True),
        ),
    ]
