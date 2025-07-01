import traceback
import uuid
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
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
    EscaladeSerializer,
)

# ---------------------------
# ViewSets accessibles sans authentification
# ---------------------------

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

# ---------------------------
# Création de ticket sans authentification
# ---------------------------

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

        serializer = TicketSerializer(data=data)
        if serializer.is_valid():
            ticket = serializer.save()
            try:
                send_mail(
                    subject="Confirmation de votre ticket",
                    message=f"Bonjour {ticket.prenom},\n\nVotre ticket a bien été enregistré.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[ticket.email],
                    fail_silently=False,
                )
                return Response({"message": "Ticket enregistré."}, status=status.HTTP_201_CREATED)
            except Exception as e:
                print(f"Email sending failed: {str(e)}")
                traceback.print_exc()
                return Response({
                    "message": "Ticket enregistré, mais l'e-mail de confirmation n'a pas pu être envoyé."
                }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------------
# Vue protégée — utilisateur connecté
# ---------------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_me(request):
    serializer = UtilisateurSerializer(request.user)
    return Response(serializer.data)

# ---------------------------
# Gestion des tickets
# ---------------------------

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [AllowAny]  # À adapter selon les rôles

    @action(detail=True, methods=["post"])
    def escalader(self, request, pk=None):
        ticket = self.get_object()
        serializer = EscaladeSerializer(data=request.data, context={"request": request, "ticket": ticket})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Ticket escaladé avec succès."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], url_path='demander-cloture')
    def demander_cloture(self, request, pk=None):
        ticket = self.get_object()

        if ticket.statut == 'cloture':
            return Response({'error': 'Le ticket est déjà clôturé.'}, status=status.HTTP_400_BAD_REQUEST)

        token = uuid.uuid4()
        ticket.confirmation_token = token
        ticket.save()

        lien_confirmation = f"http://localhost:8000/api/confirm-cloture/{token}/"

        try:
            send_mail(
                subject="Confirmation de clôture du ticket",
                message=f"Bonjour,\n\nCliquez ici pour confirmer la clôture de votre ticket : {lien_confirmation}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[ticket.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({
                'message': "Lien généré, mais l'envoi de l'e-mail a échoué.",
                'error': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Lien de confirmation envoyé au client.'}, status=status.HTTP_200_OK)

# ---------------------------
# Vue publique pour confirmer la clôture
# ---------------------------

@api_view(['GET'])
@permission_classes([AllowAny])
def confirmer_cloture(request, token):
    try:
        ticket = Ticket.objects.get(confirmation_token=token)
    except Ticket.DoesNotExist:
        return render(request, "support/confirm_cloture.html", {
            "title": "Ticket introuvable",
            "message": "Le lien de confirmation est invalide ou a expiré.",
        })

    try:
        ticket.statut = "cloture"
        ticket.date_cloture = timezone.now()
        ticket.confirmation_token = None
        ticket.save()

        return render(request, "support/confirm_cloture.html", {
            "title": "Ticket clôturé",
            "message": "Le ticket a été clôturé avec succès. Merci pour votre confirmation.",
        })

    except Exception as e:
        ticket.statut = "en_attente_confirmation"
        ticket.save()
        return render(request, "support/confirm_cloture.html", {
            "title": "Erreur lors de la clôture",
            "message": "Une erreur est survenue. Le ticket est maintenant en attente de confirmation.",
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ticket_stats(request):
    return Response({
        "total_tickets": Ticket.objects.count(),
        "tickets_en_cours": Ticket.objects.filter(statut="en_cours").count(),
        "tickets_en_attente": Ticket.objects.filter(statut="en_attente").count(),
        "tickets_clotures": Ticket.objects.filter(statut="cloture").count(),
    })
# ---------------------------
# Liste des supérieurs
# ---------------------------

class SuperieurListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        superieurs = Utilisateur.objects.filter(role="supérieur")
        serializer = UtilisateurSerializer(superieurs, many=True)
        return Response(serializer.data)
