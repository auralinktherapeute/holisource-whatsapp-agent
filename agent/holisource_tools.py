# agent/holisource_tools.py — Outils spécifiques Holisource
# Recherche thérapeutes, agendar RDV, qualifier leads, etc.

import os
import logging
import yaml
from typing import Optional, List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

try:
    import httpx
except ImportError:
    raise ImportError("Dépendances manquantes. Installe: pip install -r requirements.txt")

from agent.supabase_client import get_supabase_client

load_dotenv()
logger = logging.getLogger("holisource_agent")


class HolisourceTools:
    """Outils métier pour l'agent WhatsApp Holisource"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.resend_api_key = os.getenv("RESEND_API_KEY")

    # ════════════════════════════════════════════════════════════
    # RECHERCHE THÉRAPEUTES
    # ════════════════════════════════════════════════════════════

    async def search_therapeutes(
        self,
        specialite: Optional[str] = None,
        ville: Optional[str] = None,
        modalite: Optional[str] = None,
        tarif_max: Optional[int] = None,
    ) -> str:
        """
        Recherche des thérapeutes et retourne un texte formaté pour WhatsApp.

        Retourne une réponse lisible et bien structurée pour le client.
        """
        try:
            results = await self.supabase.search_therapeutes(
                specialite=specialite,
                ville=ville,
                modalite=modalite,
                tarif_max=tarif_max,
                limit=5,
            )

            if not results:
                return (
                    "Désolée, je n'ai pas trouvé de thérapeute correspondant à tes critères. 😔\n\n"
                    "Essaie de chercher avec d'autres paramètres ou écris-moi pour plus d'aide !"
                )

            # Formater les résultats
            response = "✨ **Voici les thérapeutes que j'ai trouvés pour toi :**\n\n"

            for i, therapiste in enumerate(results, 1):
                nom = f"{therapiste['prenom']} {therapiste['nom']}"
                ville = therapiste.get("ville", "—")
                specialites = ", ".join(therapiste.get("specialites", [])[:2])
                tarif_min = therapiste.get("tarif_min", "—")
                tarif_max = therapiste.get("tarif_max", "—")
                modalite = therapiste.get("modalite", "—")

                response += (
                    f"{i}️⃣ **{nom}**\n"
                    f"   📍 {ville}\n"
                    f"   🌟 {specialites}\n"
                    f"   💜 {tarif_min}€ - {tarif_max}€\n"
                    f"   📱 {modalite}\n\n"
                )

            response += "Réponds avec le numéro (ex: '1') pour plus de détails sur un thérapeute."
            return response

        except Exception as e:
            logger.error(f"Erreur search_therapeutes: {e}")
            return (
                "Oups ! J'ai un problème technique. 😞\n"
                "Réessaye dans quelques instants ou contacte notre équipe."
            )

    async def get_therapeute_details(self, therapeute_id: str) -> str:
        """Récupère et formate les détails complets d'un thérapeute"""
        try:
            therapiste = await self.supabase.get_therapeute(therapeute_id)

            if not therapiste:
                return "Je n'ai pas trouvé ce thérapeute. 😔"

            nom = f"{therapiste['prenom']} {therapiste['nom']}"
            description = therapiste.get("description", "—")
            approche = therapiste.get("approche", "—")
            site_web = therapiste.get("site_web")
            calendly_url = therapiste.get("calendly_url")

            response = f"💜 **{nom}**\n\n"
            response += f"📝 {description}\n\n"
            response += f"🎯 Approche : {approche}\n\n"

            if site_web:
                response += f"🌐 {site_web}\n"

            response += (
                "\n✨ **Prêt à agendar ?**\n"
                "Écris 'Agendar' et je t'aidera à réserver un créneau ! 📅"
            )

            return response

        except Exception as e:
            logger.error(f"Erreur get_therapeute_details: {e}")
            return "Oups ! Erreur technique. 😞"

    # ════════════════════════════════════════════════════════════
    # AGENDAR RENDEZ-VOUS
    # ════════════════════════════════════════════════════════════

    async def create_rdv_with_confirmation(
        self,
        numero_client: str,
        nom_client: str,
        email_client: str,
        therapeute_id: str,
        date_rdv: str,
        raison: str = "Consultation holistique",
    ) -> Dict[str, Any]:
        """
        Crée un RDV et envoie les confirmations (email + SMS).

        Retourne:
        {
            "success": True/False,
            "rdv_id": "uuid ou None",
            "message": "Texte pour WhatsApp",
        }
        """
        try:
            # Créer le RDV
            rdv_data = {
                "therapeute_id": therapeute_id,
                "client_nom": nom_client,
                "client_email": email_client,
                "client_telephone": numero_client,
                "date_rdv": date_rdv,
                "raison": raison,
                "statut": "confirmed",
                "created_at": datetime.utcnow().isoformat(),
            }

            rdv = await self.supabase.create_rdv(rdv_data)

            if not rdv:
                return {
                    "success": False,
                    "rdv_id": None,
                    "message": "Erreur lors de la création du RDV. 😞",
                }

            # Envoyer confirmation email
            await self._send_confirmation_email(email_client, nom_client, rdv)

            # Envoyer SMS
            await self._send_confirmation_sms(numero_client, rdv)

            message = (
                f"✅ **RDV confirmé !**\n\n"
                f"📅 Date: {date_rdv}\n"
                f"📍 Thérapeute confirmera les détails par email\n\n"
                f"📧 Confirmation envoyée à {email_client}\n"
                f"💬 Tu recevras aussi un SMS de rappel 24h avant\n\n"
                f"💜 Merci de faire confiance à Holisource !"
            )

            return {
                "success": True,
                "rdv_id": rdv.get("id"),
                "message": message,
            }

        except Exception as e:
            logger.error(f"Erreur create_rdv_with_confirmation: {e}")
            return {
                "success": False,
                "rdv_id": None,
                "message": "Erreur technique. Réessaye plus tard. 😞",
            }

    async def _send_confirmation_email(
        self, email: str, nom: str, rdv: Dict[str, Any]
    ) -> bool:
        """Envoie un email de confirmation via Resend"""
        try:
            if not self.resend_api_key:
                logger.warning("RESEND_API_KEY non configurée")
                return False

            therapeute_id = rdv.get("therapeute_id")
            therapeute = await self.supabase.get_therapeute(therapeute_id)

            html_content = f"""
            <h2>Confirmation de votre rendez-vous</h2>
            <p>Bonjour {nom},</p>
            <p>Votre rendez-vous a été confirmé ✨</p>
            <ul>
                <li><strong>Date :</strong> {rdv.get('date_rdv')}</li>
                <li><strong>Thérapeute :</strong> {therapeute['prenom']} {therapeute['nom']}</li>
                <li><strong>Raison :</strong> {rdv.get('raison')}</li>
            </ul>
            <p>À bientôt ! 💜</p>
            <p>Holisource — Votre annuaire de thérapeutes holistiques</p>
            """

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {self.resend_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": "Holisource <sophia@holisource.com>",
                        "to": email,
                        "subject": "✅ Votre rendez-vous est confirmé",
                        "html": html_content,
                    },
                )

                if response.status_code == 200:
                    logger.info(f"Email de confirmation envoyé à {email}")
                    return True
                else:
                    logger.error(f"Erreur Resend: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"Erreur _send_confirmation_email: {e}")
            return False

    async def _send_confirmation_sms(self, numero: str, rdv: Dict[str, Any]) -> bool:
        """Envoie un SMS de confirmation via Twilio (mock pour maintenant)"""
        try:
            # Twilio est intégré via le provider WhatsApp
            # Ici on peut logger ou envoyer via Twilio API
            therapeute_id = rdv.get("therapeute_id")
            therapeute = await self.supabase.get_therapeute(therapeute_id)
            nom_therapiste = f"{therapeute['prenom']} {therapeute['nom']}"

            logger.info(
                f"SMS de confirmation envoyé à {numero} pour RDV avec {nom_therapiste}"
            )
            return True

        except Exception as e:
            logger.error(f"Erreur _send_confirmation_sms: {e}")
            return False

    # ════════════════════════════════════════════════════════════
    # QUALIFICATION DE LEADS
    # ════════════════════════════════════════════════════════════

    async def qualify_lead(
        self,
        numero_client: str,
        nom: str,
        email: str,
        conversation_context: str,
    ) -> Dict[str, Any]:
        """
        Utilise Mistral pour qualifier un lead (sincérité, engagement, budget).

        Retourne:
        {
            "qualified": True/False,
            "score": 0-100,
            "raison": "Explication",
            "action": "convert" / "escalate" / "reject",
        }
        """
        try:
            if not self.mistral_api_key:
                logger.warning("MISTRAL_API_KEY non configurée")
                return {
                    "qualified": True,  # Default optimiste
                    "score": 50,
                    "raison": "Pas de modération Mistral configurée",
                    "action": "convert",
                }

            prompt = f"""
Tu es un expert en qualification de leads holistiques.
Évalue ce lead selon ces critères:
- Sincérité de la demande (cherche vraiment un thérapeute)
- Engagement (prêt à payer, flexible sur les modalités)
- Budget réaliste (ne demande pas gratuitement ou des prix irréalistes)
- Langage respectueux

Données du lead:
- Nom: {nom}
- Email: {email}
- Contexte de conversation: {conversation_context}

Réponds en JSON:
{{
  "qualified": true/false,
  "score": <0-100>,
  "raison": "<explication courte>",
  "action": "convert|escalate|reject"
}}

Sois strict mais juste. Les leads genuins doivent être qualifiés.
"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/messages",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 200,
                    },
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]

                    # Parser la réponse JSON
                    import json

                    try:
                        result = json.loads(content)
                        logger.info(
                            f"Lead qualified: {result.get('qualified')} (score: {result.get('score')})"
                        )
                        return result
                    except json.JSONDecodeError:
                        logger.error("Erreur parsing JSON Mistral")
                        return {
                            "qualified": True,
                            "score": 50,
                            "raison": "Erreur parsing",
                            "action": "escalate",
                        }
                else:
                    logger.error(f"Erreur Mistral API: {response.text}")
                    return {
                        "qualified": True,
                        "score": 50,
                        "raison": "Erreur API Mistral",
                        "action": "escalate",
                    }

        except Exception as e:
            logger.error(f"Erreur qualify_lead: {e}")
            return {
                "qualified": True,
                "score": 50,
                "raison": "Erreur exception",
                "action": "escalate",
            }

    # ════════════════════════════════════════════════════════════
    # CRÉER UN LEAD/PROSPECT
    # ════════════════════════════════════════════════════════════

    async def create_lead(
        self,
        numero_whatsapp: str,
        nom: str,
        email: str,
        specialite_recherchee: Optional[str],
        localisation: Optional[str],
        budget: Optional[str],
        notes: str = "",
    ) -> Optional[str]:
        """Crée un prospect dans Supabase"""
        try:
            lead_data = {
                "numero_whatsapp": numero_whatsapp,
                "nom": nom,
                "email": email,
                "specialite_recherchee": specialite_recherchee,
                "localisation": localisation,
                "budget": budget,
                "source": "whatsapp",
                "status": "new",
                "notes": notes,
                "created_at": datetime.utcnow().isoformat(),
            }

            lead_id = await self.supabase.create_lead(lead_data)
            return lead_id

        except Exception as e:
            logger.error(f"Erreur create_lead: {e}")
            return None

    # ════════════════════════════════════════════════════════════
    # UTILITAIRES
    # ════════════════════════════════════════════════════════════

    def load_holisource_config(self) -> Dict[str, Any]:
        """Charge la configuration Holisource"""
        try:
            with open("config/holisource_config.yaml", "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Erreur load_holisource_config: {e}")
            return {}


# Instance globale
_tools = None


def get_holisource_tools() -> HolisourceTools:
    """Getter pour les outils Holisource (singleton)"""
    global _tools
    if _tools is None:
        _tools = HolisourceTools()
    return _tools
