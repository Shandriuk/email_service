# Generated by Django 3.2.5 on 2021-07-15 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0004_alter_receiver_bday'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mailingreceiver',
            name='send',
        ),
        migrations.AlterField(
            model_name='mailingreceiver',
            name='send_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
