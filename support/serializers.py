from rest_framework import serializers
from .models import Societe, Prestation, DescriptionType, Role, Ticket, Utilisateur


class SocieteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Societe
        fields = ['id', 'nom']

class PrestationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prestation
        fields = ['id', 'nom', 'societe']

class DescriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DescriptionType
        fields = ['id', 'nom']

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'nom']

class TicketSerializer(serializers.ModelSerializer):
    prestation = serializers.CharField(source="prestation.nom", read_only=True)
    class Meta:
        model = Ticket
        fields = '__all__'

class UtilisateurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'nom', 'prenom', 'role']


