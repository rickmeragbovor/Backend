from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Societe, Prestation, DescriptionType, Role, Ticket, Utilisateur
from .serializers import (
    SocieteSerializer,
    PrestationSerializer,
    DescriptionTypeSerializer,
    RoleSerializer,
    TicketSerializer
)


class SocieteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Societe.objects.all()
    serializer_class = SocieteSerializer


class PrestationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prestation.objects.all()
    serializer_class = PrestationSerializer

    def get_queryset(self):
        societe_id = self.request.query_params.get('societe')
        if societe_id:
            return Prestation.objects.filter(societe_id=societe_id)
        return super().get_queryset()


class DescriptionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DescriptionType.objects.all()
    serializer_class = DescriptionTypeSerializer


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class CreateTicketView(APIView):
    def post(self, request):
        data = request.data

        # Vérification des champs requis
        required_fields = [
            "email", "nom", "prenom", "telephone", "role_client",
            "societe", "prestation", "description"
        ]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return Response(
                {"error": f"Champs manquants : {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Création ou récupération de l'utilisateur
        utilisateur, created = Utilisateur.objects.get_or_create(
            email=data["email"],
            defaults={
                "nom": data["nom"],
                "prenom": data["prenom"],
                "telephone": data["telephone"],
                "role_client": data["role_client"],
                "societe_id": data["societe"],
            },
        )

        ticket_data = {
            "client": utilisateur.id,
            "prestation": data["prestation"],
            "description": data["description"],
        }

        ticket_serializer = TicketSerializer(data=ticket_data)

        if ticket_serializer.is_valid():
            ticket = ticket_serializer.save()

            try:
                print("Tentative d'envoi de mail à :", utilisateur.email)
                send_mail(
                    subject="Confirmation de votre ticket",
                    message=f"Bonjour {utilisateur.prenom},\n\nVotre ticket a bien été enregistré.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[utilisateur.email],
                    fail_silently=False,
                )
                print("Mail envoyé avec succès")
            except Exception as e:
                print("Erreur mail :", e)

            return Response({"message": "Ticket enregistré"}, status=status.HTTP_201_CREATED)

        # Affiche les erreurs de validation
        print("Erreurs de validation :", ticket_serializer.errors)
        return Response(ticket_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
