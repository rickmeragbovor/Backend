# Generated by Django 5.2.3 on 2025-06-24 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0005_alter_ticket_statut'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='confirmation_token',
            field=models.UUIDField(blank=True, null=True, unique=True),
        ),
    ]
