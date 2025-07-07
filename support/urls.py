from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    SocieteViewSet,
    PrestationViewSet,
    DescriptionTypeViewSet,
    RoleViewSet,
    TicketViewSet, CreateTicketView, confirmer_cloture, SuperieurListAPIView, ticket_stats, UtilisateurViewSet,
)

router = DefaultRouter()
router.register(r'societes', SocieteViewSet)
router.register(r'prestations', PrestationViewSet)
router.register(r'description-types', DescriptionTypeViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'tickets', TicketViewSet)
router.register(r'utilisateurs', UtilisateurViewSet, basename='utilisateur')

urlpatterns = [
    path('', include(router.urls)),
    path('create-ticket/', CreateTicketView.as_view(), name='create-ticket'),
    path('confirm-cloture/<uuid:token>/', confirmer_cloture, name='confirmer_cloture'),
    path('superieurs/', SuperieurListAPIView.as_view(), name='liste-superieurs'),
    path('stats/',ticket_stats , name='stats'),
]

