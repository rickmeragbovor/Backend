import traceback
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Societe, Prestation, DescriptionType, Role, Ticket, Utilisateur
from .serializers import (
    SocieteSerializer,
    PrestationSerializer,
    DescriptionTypeSerializer,
    RoleSerializer,
    TicketSerializer,
    UtilisateurSerializer,
)

# ✅ Accessible sans authentification
class SocieteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Societe.objects.all()
    serializer_class = SocieteSerializer
    permission_classes = [AllowAny]

class PrestationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Prestation.objects.all()
    serializer_class = PrestationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        societe_id = self.request.query_params.get("societe")
        if societe_id:
            return Prestation.objects.filter(societe_id=societe_id)
        return super().get_queryset()

class DescriptionTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DescriptionType.objects.all()
    serializer_class = DescriptionTypeSerializer
    permission_classes = [AllowAny]

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]

# ✅ Gestion des tickets (authentification possible plus tard)
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]  # à adapter selon ton besoin plus tard

# ✅ Création de ticket sans login
class CreateTicketView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        required_fields = [
            "email", "nom", "prenom", "telephone", "role",
            "societe", "prestation", "description_type", "description"
        ]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            return Response(
                {"error": f"Champs manquants : {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket_data = {
            "nom": data["nom"],
            "prenom": data["prenom"],
            "email": data["email"],
            "telephone": data["telephone"],
            "role": data["role"],
            "societe": data["societe"],
            "prestation": data["prestation"],
            "description_type": data["description_type"],
            "description": data["description"]
        }

        ticket_serializer = TicketSerializer(data=ticket_data)

        if ticket_serializer.is_valid():
            ticket = ticket_serializer.save()
            try:
                send_mail(
                    subject="Confirmation de votre ticket",
                    message=f"Bonjour {ticket.prenom},\n\nVotre ticket a bien été enregistré.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.email],
                    fail_silently=False,
                )
                return Response({"message": "Ticket enregistré"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
                traceback.print_exc()
                return Response({
                    "message": "Ticket enregistré, mais l'email de confirmation n'a pas pu être envoyé"
                }, status=status.HTTP_201_CREATED)

        return Response(ticket_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ Vue protégée — accessible uniquement après login
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    serializer = UtilisateurSerializer(request.user)
    return Response(serializer.data)
