from rest_framework import serializers
from .models import Societe, Prestation, DescriptionType, Role, Ticket

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
    class Meta:
        model = Ticket
        fields = '__all__'
