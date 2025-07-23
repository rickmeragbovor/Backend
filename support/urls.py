from django.urls import path
from . import views

urlpatterns = [
    # === RÔLES ===
    path("roles/", views.RoleListCreateAPIView.as_view(), name="role-list-create"),

    # === UTILISATEURS ===
    path("utilisateurs/", views.UtilisateurListAPIView.as_view(), name="utilisateur-list"),
    path('utilisateurs/create/', views.UtilisateurCreateAPIView.as_view(), name='utilisateur-create'),

    # === CLIENTS ===
    path("clients/", views.ClientListCreateAPIView.as_view(), name="client-list-create"),
    path("clients/<int:pk>/", views.ClientDetailAPIView.as_view(), name="client-detail"),

    # === PERSONNELS ===
    path("personnels/", views.PersonnelListAPIView.as_view(), name="personnel-list"),
    path('personnels/create/', views.PersonnelCreateAPIView.as_view(), name='personnel-create'),


    # === PERSONNEL - CLIENT ===
    path("personnel-clients/", views.PersonnelClientListCreateAPIView.as_view(), name="personnel-client-list-create"),
    path("personnel-clients/<int:pk>/", views.PersonnelClientDetailAPIView.as_view(), name="personnel-client-detail"),

    # === TYPES LOGICIELS ET PROBLEMES ===
    path("types-logiciels/", views.TypeLogicielListCreateAPIView.as_view(), name="type-logiciel-list-create"),
    path("types-problemes/", views.TypeProblemeListCreateAPIView.as_view(), name="type-probleme-list-create"),

    # === LOGICIELS ===
    path("logiciels/", views.LogicielListCreateAPIView.as_view(), name="logiciel-list-create"),
    path("logiciels/<int:pk>/", views.LogicielDetailAPIView.as_view(), name="logiciel-detail"),

    # === TICKETS ===
    path("tickets/", views.TicketListCreateAPIView.as_view(), name="ticket-list-create"),
    path("tickets/<int:pk>/", views.TicketDetailAPIView.as_view(), name="ticket-detail"),
    ###GPTS TICKETS
    path("mes-tickets/", views.MesTicketsAPIView.as_view(), name="mes-tickets"),

    # === RAPPORTS ===
    path("rapports/", views.RapportListCreateAPIView.as_view(), name="rapport-list-create"),

    # === FICHIERS ===
    path("fichiers/", views.FichierListAPIView.as_view(), name="fichier-list"),

    # === Profile ===
    path('me/', views.MeAPIView.as_view(), name='me'),
]
