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
# UTILISATEUR : uniquement les techniciens se connectent
# -------------------------
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

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
# PRESTATION : liée à une société
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
    nom = models.CharField(max_length=100)  # ex: "Problème réseau", "Imprimante", "Autre"

    def __str__(self):
        return self.nom

# -------------------------
# RÔLES DANS LA SOCIÉTÉ
# -------------------------
class Role(models.Model):
    nom = models.CharField(max_length=100)  # ex: "Responsable IT", "Utilisateur", "Autre"

    def __str__(self):
        return self.nom

# -------------------------
# TICKET DE SUPPORT CLIENT
# -------------------------
class Ticket(models.Model):
    # Informations du client
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)

    # Informations liées à la société et prestation
    societe = models.ForeignKey(Societe, on_delete=models.SET_NULL, null=True)
    prestation = models.ForeignKey(Prestation, on_delete=models.SET_NULL, null=True)

    # Description du problème
    description_type = models.ForeignKey(DescriptionType, on_delete=models.SET_NULL, null=True, blank=True)

    # Poste ou rôle dans l'entreprise
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    # Suivi
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default="En attente")  # En attente, En cours, Résolu...
    technicien = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.nom} {self.prenom} - {self.societe}"
