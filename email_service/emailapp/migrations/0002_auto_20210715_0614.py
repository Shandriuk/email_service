# Generated by Django 3.2.5 on 2021-07-15 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('emailapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='mailing_body',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='mailing',
            name='mailing_signature',
            field=models.TextField(default=''),
        ),
    ]
