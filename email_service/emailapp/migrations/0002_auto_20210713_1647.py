# Generated by Django 3.2.5 on 2021-07-13 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailingreceiver',
            name='received',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='mailingreceiver',
            name='send',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='mailing',
            name='mailing_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='mailingreceiver',
            name='received_date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='mailingreceiver',
            name='send_date',
            field=models.DateTimeField(blank=True),
        ),
    ]
