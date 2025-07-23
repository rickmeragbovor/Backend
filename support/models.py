from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# === User Manager ===

class UserManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        if not email:
            raise ValueError("Adresse email obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        user = self.create_user(email, nom, prenom, password, **extra_fields)

        role, _ = Role.objects.get_or_create(nom="superadmin")
        user.roles.add(role)

        return user


# === Role ===

class Role(models.Model):
    nom = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nom


# === Utilisateur ===

class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    tel = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    roles = models.ManyToManyField(Role, related_name="utilisateurs")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    objects = UserManager()

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def has_role(self, nom):
        return self.roles.filter(nom=nom).exists()


# === Client ===

class Client(models.Model):
    TYPES = (
        ("PROJET", "Projet"),
        ("SOCIETE", "Société"),
    )
    nom = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=TYPES, default="SOCIETE")

    def __str__(self):
        return f"{self.nom} ({self.type})"


# === Personnel (profil avec poste) ===

class Personnel(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        limit_choices_to={"roles__nom": "personnel"},
        related_name="profil_personnel"
    )
    poste = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.utilisateur.get_full_name()} - {self.poste}"


# === Lien personnel <-> client ===

class PersonnelClient(models.Model):
    personnel = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        limit_choices_to={"roles__nom": "personnel"},
        related_name="clients_rattaches"
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="personnels_rattaches"
    )

    def __str__(self):
        return f"{self.personnel.get_full_name()} <-> {self.client.nom}"


# === Types logiciels et problèmes ===

class TypeLogiciel(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


class TypeProbleme(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom


# === Logiciel ===

class Logiciel(models.Model):
    nom = models.CharField(max_length=100)
    type_logiciel = models.ForeignKey(TypeLogiciel, on_delete=models.CASCADE)
    type_problemes = models.ManyToManyField(TypeProbleme, related_name="logiciels")

    def __str__(self):
        return self.nom


# === Ticket ===

class Ticket(models.Model):
    STATUTS = [
        ("en_attente", "En attente"),
        ("en_cours", "En cours"),
        ("clos", "Clôturé"),
    ]

    lien = models.ForeignKey(
        PersonnelClient,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    technicien = models.ForeignKey(
        Utilisateur,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"roles__nom": "technicien"},
        related_name="tickets_assignes"
    )
    logiciel = models.ForeignKey(Logiciel, on_delete=models.CASCADE)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUTS, default="en_attente")
    date_creation = models.DateField(auto_now_add=True)
    date_cloture = models.DateField(null=True, blank=True)
    temps_traitement = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.lien.client.nom}"


# === Rapport ===

class Rapport(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    contenu = models.TextField()

    def __str__(self):
        return f"Rapport - Ticket #{self.ticket.id}"


# === Fichier joint ===

class Fichier(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="fichiers"
    )
    fichier = models.FileField(upload_to="tickets/fichiers/")
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fichier.name
