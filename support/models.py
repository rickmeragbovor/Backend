from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# -------------------------
# MANAGER UTILISATEUR
# -------------------------
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

# -------------------------
# UTILISATEUR
# -------------------------
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    ROLE_CHOICES = (
        ("admin", "Administrateur"),
        ("technicien", "Technicien"),
        ("supérieur", "Supérieur"),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="technicien")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = UserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

# -------------------------
# SOCIÉTÉ
# -------------------------
class Societe(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# -------------------------
# PRESTATION
# -------------------------
class Prestation(models.Model):
    societe = models.ForeignKey(Societe, on_delete=models.CASCADE, related_name="prestations")
    nom = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nom} - {self.societe.nom}"

# -------------------------
# TYPES DE DESCRIPTION DE PROBLÈME
# -------------------------
class DescriptionType(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# -------------------------
# RÔLES DANS LA SOCIÉTÉ
# -------------------------
class Role(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# -------------------------
# TICKET DE SUPPORT CLIENT
# -------------------------
class Ticket(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("en_cours", "En cours"),
        ("en_attente_confirmation", "En attente de confirmation"),
        ("cloture", "Clôturé"),
    ]

    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    societe = models.ForeignKey(Societe, on_delete=models.SET_NULL, null=True)
    prestation = models.ForeignKey(Prestation, on_delete=models.SET_NULL, null=True)
    description_type = models.ForeignKey(DescriptionType, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default="en_attente")
    technicien = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    confirmation_token = models.UUIDField(null=True, blank=True, unique=True)

    # Champs d’escalade
    escalade_vers = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets_escalades"
    )
    niveau_escalade = models.PositiveIntegerField(default=0)

    def escalader(self, utilisateur, superieur, commentaire=""):
        self.escalade_vers = superieur
        self.niveau_escalade += 1
        self.save()

        EscaladeHistorique.objects.create(
            ticket=self,
            utilisateur=utilisateur,
            superieur=superieur,
            commentaire=commentaire,
        )

    def __str__(self):
        return f"Ticket #{self.id} - {self.nom} {self.prenom} - {self.societe}"

# -------------------------
# HISTORIQUE D'ESCALADE
# -------------------------
class EscaladeHistorique(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="escalades")
    utilisateur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, related_name="escalades_effectuees"
    )
    superieur = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, related_name="escalades_recues"
    )
    commentaire = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.date:%Y-%m-%d %H:%M}] {self.utilisateur} → {self.superieur} (Ticket #{self.ticket.id})"

# -------------------------
# RAPPORT DE CLÔTURE
# -------------------------
class Rapport(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE, related_name="rapport")
    technicien = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    resume = models.TextField()
    actions_menees = models.TextField()
    date_cloture = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rapport Ticket #{self.ticket.id} - {self.technicien.prenom} {self.technicien.nom}"
