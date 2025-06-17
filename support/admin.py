from django.contrib import admin
from .models import Societe, Prestation, DescriptionType, Role, Ticket, Utilisateur

admin.site.register(Societe)
admin.site.register(Prestation)
admin.site.register(DescriptionType)
admin.site.register(Role)
admin.site.register(Ticket)
admin.site.register(Utilisateur)
