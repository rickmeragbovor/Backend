# dans ton_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .views import (
    SocieteViewSet,
    PrestationViewSet,
    DescriptionTypeViewSet,
    RoleViewSet,
    TicketViewSet, CreateTicketView, confirmer_cloture, SuperieurListAPIView, ticket_stats,
)

router = DefaultRouter()
router.register(r'societes', SocieteViewSet)
router.register(r'prestations', PrestationViewSet)
router.register(r'description-types', DescriptionTypeViewSet)
router.register(r'roles', RoleViewSet)
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-ticket/', CreateTicketView.as_view(), name='create-ticket'),
    path('confirm-cloture/<uuid:token>/', confirmer_cloture, name='confirmer_cloture'),
    path('utilisateurs/', SuperieurListAPIView.as_view(), name='liste-superieurs'),
    path('stats/',ticket_stats , name='stats'),
]

