from rest_framework import serializers
from .models import Societe, Prestation, DescriptionType, Role, Ticket, Utilisateur, EscaladeHistorique


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

from rest_framework import serializers
from .models import Utilisateur  # ou ton modèle CustomUser
class UtilisateurSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Utilisateur
        fields = ['id', 'prenom', 'nom', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        current_user = request.user if request else None

        # Gestion du rôle (sécurité)
        role_donne = validated_data.get('role', 'technicien')

        if current_user and current_user.role in ['administrateur', 'superieur']:
            # autorisé à créer tous les rôles
            pass
        else:
            # si pas autorisé, on force à technicien
            role_donne = 'technicien'

        validated_data['role'] = role_donne

        password = validated_data.pop('password')
        user = Utilisateur(**validated_data)
        user.set_password(password)  # Hash du mot de passe
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Mise à jour des champs simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Mise à jour du mot de passe si fourni
        if password:
            instance.set_password(password)

        instance.save()
        return instance

    def to_representation(self, instance):
        """ Personnalisation du retour (hide fields if needed) """
        representation = super().to_representation(instance)
        # On pourrait par exemple ne pas retourner le rôle à certains utilisateurs
        return representation

class TicketSerializer(serializers.ModelSerializer):
    # Champs en écriture : on attend un ID
    societe = serializers.PrimaryKeyRelatedField(queryset=Societe.objects.all(), write_only=True)
    prestation = serializers.PrimaryKeyRelatedField(queryset=Prestation.objects.all(), write_only=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), write_only=True)
    description_type = serializers.PrimaryKeyRelatedField(queryset=DescriptionType.objects.all(), write_only=True)

    # Champs en lecture seule : détails complets pour GET
    societe_detail = SocieteSerializer(source='societe', read_only=True)
    prestation_detail = PrestationSerializer(source='prestation', read_only=True)
    role_detail = RoleSerializer(source='role', read_only=True)
    description_type_detail = DescriptionTypeSerializer(source='description_type', read_only=True)

    technicien = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            'id',
            'nom',
            'prenom',
            'email',
            'telephone',
            'societe',
            'prestation',
            'description_type',
            'role',
            'societe_detail',
            'prestation_detail',
            'role_detail',
            'description_type_detail',
            'date_creation',
            'statut',
            'technicien',
        ]

class EscaladeSerializer(serializers.Serializer):
    superieur_id = serializers.PrimaryKeyRelatedField(queryset=Utilisateur.objects.filter(role="supérieur"))
    commentaire = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate(self, attrs):
        ticket = self.context['ticket']
        superieur = attrs['superieur_id']

        if ticket.escalade_vers == superieur:
            raise serializers.ValidationError("Le ticket est déjà escaladé vers ce supérieur.")
        return attrs

    def save(self):
        ticket = self.context['ticket']
        utilisateur = self.context['request'].user
        superieur = self.validated_data['superieur_id']
        commentaire = self.validated_data.get('commentaire', '')

        ticket.escalader(utilisateur=utilisateur, superieur=superieur, commentaire=commentaire)
        return ticket
