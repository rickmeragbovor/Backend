# Generated by Django 5.2.3 on 2025-07-10 21:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('support', '0011_ticket_escalade_vers_ticket_niveau_escalade_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='statut',
            field=models.CharField(choices=[('en_attente', 'En attente'), ('escaladé', 'Escaladé'), ('en_attente_confirmation', 'En attente de confirmation'), ('cloture', 'Clôturé')], default='en_attente', max_length=50),
        ),
    ]
