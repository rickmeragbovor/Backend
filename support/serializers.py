from .models import Societe, Prestation, DescriptionType, Role, Ticket, EscaladeHistorique
from rest_framework import serializers
from .models import Utilisateur

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
        current_user = request.user if request and request.user.is_authenticated else None

        role_donne = validated_data.get('role', 'technicien')
        print("Current user:", current_user)
        print("Role demandé:", role_donne)

        if not current_user or current_user.role not in ['admin', 'supérieur']:
            role_donne = 'technicien'

        validated_data['role'] = role_donne

        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Ce champ est obligatoire."})

        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        request = self.context.get('request')
        current_user = request.user if request and request.user.is_authenticated else None
        password = validated_data.pop('password', None)
        new_password = password.strip() if password else None
        # 🔒 Gestion sécurisée du champ role
        if 'role' in validated_data:
            if not current_user or current_user.role not in ['admin', 'supérieur']:
                validated_data.pop('role')
        # Mise à jour des champs simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # Gestion du mot de passe
        if new_password:
            if not instance.check_password(new_password):
                instance.set_password(new_password)
            else:
                print("ℹ Le mot de passe est identique à l'existant, pas de mise à jour.")
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
    superieur_id = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.filter(role="supérieur"),
        source="superieur"  # mappe vers un objet Utilisateur
    )
    commentaire = serializers.CharField(
        required=False, allow_blank=True, max_length=500
    )

    def validate(self, attrs):
        ticket = self.context['ticket']
        superieur = attrs['superieur']
        if ticket.escalade_vers == superieur:
            raise serializers.ValidationError("Le ticket est déjà escaladé vers ce supérieur.")
        return attrs

    def save(self):
        ticket = self.context['ticket']
        utilisateur = self.context['request'].user
        superieur = self.validated_data['superieur']
        commentaire = self.validated_data.get('commentaire', '')
        ticket.escalader(utilisateur=utilisateur, superieur=superieur, commentaire=commentaire)
        return ticket