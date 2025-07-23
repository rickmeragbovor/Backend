from django.contrib import admin
from .models import Client, PersonnelClient ,Personnel, TypeLogiciel,TypeProbleme,Ticket,Logiciel,Utilisateur,Fichier,Role,Rapport

admin.site.register(Client),
admin.site.register(PersonnelClient),
admin.site.register(Personnel),
admin.site.register(TypeLogiciel),
admin.site.register(TypeProbleme),
admin.site.register(Ticket),
admin.site.register(Logiciel),
admin.site.register(Utilisateur),
admin.site.register(Fichier),
admin.site.register(Role),
admin.site.register(Rapport),


