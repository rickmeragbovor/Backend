# Generated by Django 5.2.3 on 2025-07-16 07:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('PROJET', 'Projet'), ('SOCIETE', 'Société')], default='SOCIETE', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Logiciel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TypeLogiciel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TypeProbleme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Utilisateur',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('nom', models.CharField(max_length=50)),
                ('prenom', models.CharField(max_length=50)),
                ('tel', models.CharField(blank=True, max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
                ('roles', models.ManyToManyField(related_name='utilisateurs', to='support.role')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Personnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('poste', models.CharField(max_length=50)),
                ('utilisateur', models.OneToOneField(limit_choices_to={'roles__nom': 'personnel'}, on_delete=django.db.models.deletion.CASCADE, related_name='profil_personnel', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PersonnelClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='personnels_rattaches', to='support.client')),
                ('personnel', models.ForeignKey(limit_choices_to={'roles__nom': 'personnel'}, on_delete=django.db.models.deletion.CASCADE, related_name='clients_rattaches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('statut', models.CharField(choices=[('en_attente', 'En attente'), ('en_cours', 'En cours'), ('clos', 'Clôturé')], default='en_attente', max_length=20)),
                ('date_creation', models.DateField(auto_now_add=True)),
                ('date_cloture', models.DateField(blank=True, null=True)),
                ('temps_traitement', models.DurationField(blank=True, null=True)),
                ('lien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='support.personnelclient')),
                ('logiciel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='support.logiciel')),
                ('technicien', models.ForeignKey(blank=True, limit_choices_to={'roles__nom': 'technicien'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tickets_assignes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rapport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('contenu', models.TextField()),
                ('ticket', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='support.ticket')),
            ],
        ),
        migrations.CreateModel(
            name='Fichier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='tickets/fichiers/')),
                ('date_ajout', models.DateTimeField(auto_now_add=True)),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fichiers', to='support.ticket')),
            ],
        ),
        migrations.AddField(
            model_name='logiciel',
            name='type_logiciel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='support.typelogiciel'),
        ),
        migrations.AddField(
            model_name='logiciel',
            name='type_problemes',
            field=models.ManyToManyField(related_name='logiciels', to='support.typeprobleme'),
        ),
    ]
