from rest_framework import serializers
from .models import (
    Role, Utilisateur, Client, Personnel, PersonnelClient,
    TypeLogiciel, TypeProbleme, Logiciel,
    Ticket, Rapport, Fichier
)

# === Role ===
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'nom']


# === Utilisateur ===
class UtilisateurSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    clients = serializers.SerializerMethodField()

    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'nom', 'prenom', 'tel', 'roles', 'clients']

    def get_clients(self, obj):
        if obj.has_role("personnel"):
            links = PersonnelClient.objects.filter(personnel=obj).select_related("client")
            return [
                {
                    "id": link.client.id,
                    "nom": link.client.nom,
                    "type": link.client.type,
                }
                for link in links
            ]
        return []

class UtilisateurCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    roles = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), many=True)

    class Meta:
        model = Utilisateur
        fields = ['email', 'nom', 'prenom', 'tel', 'password', 'roles']

    def create(self, validated_data):
        roles_data = validated_data.pop('roles')
        password = validated_data.pop('password')

        # Création de l'utilisateur avec son password sécurisé
        user = Utilisateur.objects.create_user(password=password, **validated_data)

        # Attribution des rôles
        user.roles.set(roles_data)
        return user


# === Client ===
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'nom', 'type']


# === Personnel ===
class PersonnelSerializer(serializers.ModelSerializer):
    utilisateur = UtilisateurSerializer(read_only=True)

    class Meta:
        model = Personnel
        fields = ['id', 'utilisateur', 'poste']

class PersonnelCreateSerializer(serializers.ModelSerializer):
    utilisateur = serializers.PrimaryKeyRelatedField(
        queryset=Utilisateur.objects.filter(roles__nom="personnel")
    )

    class Meta:
        model = Personnel
        fields = ['utilisateur', 'poste']



# === PersonnelClient ===
class PersonnelClientSerializer(serializers.ModelSerializer):
    personnel = UtilisateurSerializer(read_only=True)
    client = ClientSerializer(read_only=True)

    class Meta:
        model = PersonnelClient
        fields = ['id', 'personnel', 'client']

class PersonnelClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelClient
        fields = ['id', 'personnel', 'client']

# === TypeLogiciel ===
class TypeLogicielSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeLogiciel
        fields = ['id', 'nom']


# === TypeProbleme ===
class TypeProblemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeProbleme
        fields = ['id', 'nom']


# === Logiciel ===
class LogicielSerializer(serializers.ModelSerializer):
    type_logiciel = TypeLogicielSerializer(read_only=True)
    type_problemes = TypeProblemeSerializer(many=True, read_only=True)

    class Meta:
        model = Logiciel
        fields = ['id', 'nom', 'type_logiciel', 'type_problemes']


class LogicielCreateSerializer(serializers.ModelSerializer):
    type_problemes = serializers.PrimaryKeyRelatedField(
        many=True, queryset=TypeProbleme.objects.all()
    )

    class Meta:
        model = Logiciel
        fields = ['id', 'nom', 'type_logiciel', 'type_problemes']


# === Fichier ===
class FichierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fichier
        fields = ['id', 'fichier', 'date_ajout']


# === Rapport ===
class RapportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rapport
        fields = ['id', 'ticket', 'date', 'contenu']


# === Ticket ===
class TicketReadSerializer(serializers.ModelSerializer):
    lien = PersonnelClientSerializer(read_only=True)
    technicien = UtilisateurSerializer(read_only=True)
    logiciel = LogicielSerializer(read_only=True)
    fichiers = FichierSerializer(many=True, read_only=True)
    rapport = RapportSerializer(read_only=True, required=False)

    class Meta:
        model = Ticket
        fields = [
            'id', 'lien', 'technicien', 'logiciel',
            'description', 'statut',
            'date_creation', 'date_cloture', 'temps_traitement',
            'fichiers', 'rapport'
        ]


#####################
class FichierSerializer(serializers.ModelSerializer):
    ticket = TicketReadSerializer()

    class Meta:
        model = Fichier
        fields = ['id', 'fichier', 'date_ajout', 'ticket']


class TicketWriteSerializer(serializers.ModelSerializer):
    fichiers = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'lien', 'technicien', 'logiciel',
            'description', 'statut', 'fichiers'
        ]

    def create(self, validated_data):
        fichiers_data = validated_data.pop('fichiers', [])
        ticket = Ticket.objects.create(**validated_data)

        for fichier in fichiers_data:
            Fichier.objects.create(ticket=ticket, fichier=fichier)

        return ticket


# === Profile ==

class MeSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    poste = serializers.SerializerMethodField()

    class Meta:
        model = Utilisateur
        fields = ['id', 'email', 'nom', 'prenom', 'tel', 'roles', 'poste']

    def get_poste(self, obj):
        if obj.roles.filter(nom="personnel").exists():
            try:
                return obj.profil_personnel.poste
            except Personnel.DoesNotExist:
                return None
        return None