from django.core.mail import send_mail
from django.conf import settings

from support.models import Utilisateur


# 🔢 Formatage du numéro de ticket
def format_ticket_id(ticket_id: int) -> str:
    return f"TKK{ticket_id:05d}"


def envoyer_mail_prise_en_charge(ticket):
    destinataire = ticket.lien.personnel.email
    sujet = f"Votre ticket {format_ticket_id(ticket.id)} a été pris en charge"
    message = (
        f"Bonjour {ticket.lien.personnel.get_full_name()},\n\n"
        f"Votre ticket {format_ticket_id(ticket.id)} concernant le client {ticket.lien.client.nom} "
        f"et le logiciel {ticket.logiciel.nom} a été pris en charge par notre équipe support.\n\n"
        f"Description du problème :\n{ticket.description}\n\n"
        f"Nous reviendrons vers vous dès que possible.\n\n"
        f"Merci,\nL'équipe support TechExpert"
    )
    send_mail(sujet, message, settings.DEFAULT_FROM_EMAIL, [destinataire], fail_silently=False)



def envoyer_mail_creation_ticket(ticket):
    sujet = f"[Nouveau Ticket] {format_ticket_id(ticket.id)} – {ticket.lien.client.nom}"

    message = (
        f"Un nouveau ticket a été créé par {ticket.lien.personnel.get_full_name()}.\n\n"
        f"Client : {ticket.lien.client.nom} ({ticket.lien.client.type})\n"
        f"Logiciel : {ticket.logiciel.nom}\n"
        f"Description : {ticket.description}\n\n"
        f"Statut : {ticket.statut}\n"
        f"Date : {ticket.date_creation.strftime('%d/%m/%Y')}\n\n"
        f"Merci de le prendre en charge rapidement.\n\n"
        f"- Système de ticket TechExpert"
    )

    # 🔍 Chercher tous les administrateurs et superviseurs
    destinataires = list(
        Utilisateur.objects.filter(roles__nom__in=["administrateur", "superviseur"])
        .values_list("email", flat=True)
        .distinct()
    )

    if destinataires:
        send_mail(
            sujet,
            message,
            settings.DEFAULT_FROM_EMAIL,
            destinataires,
            fail_silently=False
        )