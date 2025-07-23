from rest_framework import generics, permissions
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Role, Utilisateur, Client, Personnel, PersonnelClient,
    TypeLogiciel, TypeProbleme, Logiciel,
    Ticket, Rapport, Fichier
)
from .serializers import (
    RoleSerializer, UtilisateurSerializer, ClientSerializer, PersonnelSerializer,
    PersonnelClientSerializer, TypeLogicielSerializer, TypeProblemeSerializer, MeSerializer,
    LogicielSerializer, TicketReadSerializer, TicketWriteSerializer,
    RapportSerializer, FichierSerializer, UtilisateurCreateSerializer, PersonnelCreateSerializer, PersonnelClientCreateSerializer
)
from .utils import envoyer_mail_creation_ticket


# === BASE PERMISSION ===
class IsAuthenticated(permissions.IsAuthenticated):
    pass


# === ROLES ===
class RoleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]


# === UTILISATEUR ===
class UtilisateurListAPIView(generics.ListAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurSerializer
    permission_classes = [IsAuthenticated]

class UtilisateurCreateAPIView(generics.CreateAPIView):
    queryset = Utilisateur.objects.all()
    serializer_class = UtilisateurCreateSerializer
    permission_classes = [permissions.AllowAny]

# === CLIENT ===
class ClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


class ClientDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]


# === PERSONNEL ===
class PersonnelListAPIView(generics.ListAPIView):
    queryset = Personnel.objects.select_related('utilisateur')
    serializer_class = PersonnelSerializer
    permission_classes = [IsAuthenticated]

class PersonnelCreateAPIView(generics.CreateAPIView):
    queryset = Personnel.objects.all()
    serializer_class = PersonnelCreateSerializer
    permission_classes = [permissions.IsAuthenticated]


# === PERSONNELCLIENT ===
class PersonnelClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = PersonnelClient.objects.all().select_related("client")
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        personnel_id = self.request.query_params.get("personnel_id")

        if personnel_id:
            return PersonnelClient.objects.filter(personnel__id=personnel_id).select_related("client")
        # Par défaut : l'utilisateur connecté
        return PersonnelClient.objects.filter(personnel=self.request.user).select_related("client")

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PersonnelClientCreateSerializer
        return PersonnelClientSerializer


class PersonnelClientDetailAPIView(generics.RetrieveDestroyAPIView):
    queryset = PersonnelClient.objects.all()
    serializer_class = PersonnelClientSerializer
    permission_classes = [IsAuthenticated]


# === TYPE LOGICIEL ===
class TypeLogicielListCreateAPIView(generics.ListCreateAPIView):
    queryset = TypeLogiciel.objects.all()
    serializer_class = TypeLogicielSerializer
    permission_classes = [IsAuthenticated]


# === TYPE PROBLEME ===

class TypeProblemeListCreateAPIView(generics.ListCreateAPIView):
    queryset = TypeProbleme.objects.all()
    serializer_class = TypeProblemeSerializer
    permission_classes = [IsAuthenticated]


# === LOGICIEL ===
class LogicielListCreateAPIView(generics.ListCreateAPIView):
    queryset = Logiciel.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return LogicielSerializer  # tu peux remplacer par LogicielCreateSerializer si besoin
        return LogicielSerializer


class LogicielDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Logiciel.objects.all()
    serializer_class = LogicielSerializer
    permission_classes = [IsAuthenticated]


# === TICKET ===
class TicketListCreateAPIView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TicketWriteSerializer
        return TicketReadSerializer

    def perform_create(self, serializer):
        ticket = serializer.save()
        envoyer_mail_prise_en_charge(ticket)
        envoyer_mail_creation_ticket(ticket)  # Notifie admin et superviseur


class TicketDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketReadSerializer
    permission_classes = [IsAuthenticated]


# === RAPPORT ===
class RapportListCreateAPIView(generics.ListCreateAPIView):
    queryset = Rapport.objects.all()
    serializer_class = RapportSerializer
    permission_classes = [IsAuthenticated]


# === FICHIER ===
class FichierListAPIView(generics.ListAPIView):
    queryset = Fichier.objects.all()
    serializer_class = FichierSerializer
    permission_classes = [IsAuthenticated]


# === PROFILE ===
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

##""" GPT URL FOR TICKETS

class MesTicketsAPIView(ListAPIView):
    serializer_class = TicketReadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(lien__personnel=self.request.user).select_related("lien__client", "logiciel")

####mailling
# Code Python pour envoyer un email depuis Django (backend)

from django.core.mail import send_mail
from django.conf import settings

from django.core.mail import send_mail

def envoyer_mail_prise_en_charge(ticket):
    personnel = ticket.lien.personnel
    destinataire = personnel.email
    sujet = "Votre ticket a été pris en charge"

    message = (
        f"Bonjour {personnel.get_full_name()},\n\n"
        f"Votre ticket TKK00{ticket.id} concernant le client {ticket.lien.client.nom} "
        f"et le logiciel {ticket.logiciel.nom} a été pris en charge par notre équipe support.\n\n"
        f"📝 Description du problème :\n{ticket.description}\n\n"
        f"Nous reviendrons vers vous dès que possible.\n\n"
        f"Merci,\nL'équipe support TECHEXPERT SARL"
    )

    send_mail(
        sujet,
        message,
        None,  # utilise DEFAULT_FROM_EMAIL comme expéditeur
        [destinataire],
        fail_silently=False,
    )

