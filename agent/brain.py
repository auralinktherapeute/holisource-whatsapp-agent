# agent/brain.py — Cerveau IA de l'agent Holisource
# Intégration Claude API + Holisource Tools

import os
import logging
import yaml
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

try:
    from mistralai.client.sdk import Mistral
    from mistralai.client.models.systemmessage import SystemMessage
    from mistralai.client.models.usermessage import UserMessage
    from mistralai.client.models.assistantmessage import AssistantMessage
except ImportError:
    raise ImportError("mistralai non installé. Installe avec: pip install mistralai")

from agent.holisource_tools import get_holisource_tools
from agent.supabase_client import get_supabase_client

load_dotenv()
logger = logging.getLogger("holisource_agent")

# Client Mistral
client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def load_system_prompt() -> str:
    """Charge le system prompt Holisource depuis prompts.yaml"""
    try:
        with open("config/prompts_holisource.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
            return config.get("system_prompt", _default_system_prompt())
    except FileNotFoundError:
        logger.warning("prompts_holisource.yaml non trouvé, utilisant le prompt par défaut")
        return _default_system_prompt()


def _default_system_prompt() -> str:
    """System prompt par défaut (en cas d'absence du fichier de config)"""
    return """Tu es Sofia, l'assistante virtuelle de Holisource.

Holisource est un annuaire de thérapeutes holistiques en Alsace (Bas-Rhin 67 + Haut-Rhin 68).

## Ta mission
Aider les patients à trouver le bon thérapeute holistique et agendar leurs rendez-vous.

## Tes capacités
1. Rechercher des thérapeutes (par spécialité, localité, modalité, budget)
2. Agendar des rendez-vous via Calendly
3. Répondre aux questions sur les services holistiques
4. Qualifier les leads (déterminer si le patient est sincère et engagé)
5. Créer des prospects/leads pour escalade commerciale

## Tone
Empathique, professionnel, chaleureux. En français toujours.
Utilise 💜 (violet Holisource) et ✨ (magie) sparingly.

## Règles
- JAMAIS inventer de thérapeutes
- JAMAIS partager les emails directs
- Demander le consentement avant d'agendar
- Proposer "Créer mon profil" aux nouveaux thérapeutes
- Si tu ne sais pas quelque chose: "Je vais t'aider à trouver la bonne personne"

## Interactions prioritaires
1. Si client cherche thérapeute → SEARCH
2. Si client veut agendar → CONFIRMATION
3. Si client pose une question → RÉPONDRE simplement
4. Si client semble non sincère → QUALIFIER et possiblement ESCALADER

Sois utile, honnête et bienveillant."""


class HolisourceBrain:
    """Moteur IA pour Holisource"""

    def __init__(self):
        self.tools = get_holisource_tools()
        self.supabase = get_supabase_client()
        self.system_prompt = load_system_prompt()

    async def generate_response(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        numero_client: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Génère une réponse pour le client.

        Args:
            user_message: Le message du client
            chat_history: Historique de la conversation
            numero_client: Le numéro WhatsApp du client
            context: Contexte additionnel (nom, email, etc.)

        Returns:
            La réponse à envoyer au client
        """
        try:
            # Construire les messages pour Mistral
            messages = [SystemMessage(content=self.system_prompt)]

            # Ajouter l'historique
            for msg in chat_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "assistant":
                    messages.append(AssistantMessage(content=content))
                else:
                    messages.append(UserMessage(content=content))

            # Ajouter le message courant
            messages.append(UserMessage(content=user_message))

            # Appel Mistral API
            response = await client.chat.complete_async(
                model="mistral-large-latest",
                max_tokens=1024,
                messages=messages
            )

            respuesta = response.choices[0].message.content

            # Log la conversation
            await self.supabase.log_chat_message(
                numero_client,
                "user",
                user_message,
                metadata=context or {}
            )
            await self.supabase.log_chat_message(
                numero_client,
                "assistant",
                respuesta,
            )

            logger.info(
                f"Réponse générée (Mistral {response.model})"
            )
            return respuesta

        except Exception as e:
            logger.error(f"Erreur Mistral API: {e}")
            return (
                "Oups ! J'ai un problème technique. 😞\n"
                "Réessaye dans quelques instants ou contacte notre équipe à contact@holisource.com"
            )

    async def handle_search_request(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]],
        numero_client: str,
    ) -> str:
        """
        Gère une demande de recherche de thérapeute.
        Extrait les critères du message et retourne les résultats.
        """
        try:
            # Utiliser Claude pour extraire les paramètres
            extraction_prompt = f"""
Extrait les critères de recherche du message client en JSON:
- specialite (string ou null)
- ville (string ou null)
- modalite ("presentiel" | "distanciel" | "les_deux" ou null)
- tarif_max (int ou null)

Message: "{user_message}"

Réponds UNIQUEMENT du JSON, ex:
{{"specialite": "reiki", "ville": "Strasbourg", "modalite": "les_deux", "tarif_max": 80}}
"""

            response = await client.chat.complete_async(
                model="mistral-large-latest",
                max_tokens=200,
                messages=[UserMessage(content=extraction_prompt)]
            )

            import json
            try:
                criteria = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                criteria = {}

            # Rechercher les thérapeutes
            result = await self.tools.search_therapeutes(
                specialite=criteria.get("specialite"),
                ville=criteria.get("ville"),
                modalite=criteria.get("modalite"),
                tarif_max=criteria.get("tarif_max"),
            )

            # Log
            await self.supabase.log_chat_message(
                numero_client,
                "assistant",
                result,
                metadata={"action": "search", "criteria": criteria}
            )

            return result

        except Exception as e:
            logger.error(f"Erreur handle_search_request: {e}")
            return (
                "Désolée, j'ai eu un souci en cherchant les thérapeutes. 😞\n"
                "Réessaye ou contacte notre équipe."
            )

    async def handle_rdv_request(
        self,
        therapeute_id: str,
        nom_client: str,
        email_client: str,
        numero_client: str,
        date_rdv: str,
    ) -> str:
        """
        Gère la création d'un rendez-vous.
        """
        try:
            result = await self.tools.create_rdv_with_confirmation(
                numero_client=numero_client,
                nom_client=nom_client,
                email_client=email_client,
                therapeute_id=therapeute_id,
                date_rdv=date_rdv,
            )

            if result["success"]:
                await self.supabase.log_chat_message(
                    numero_client,
                    "system",
                    f"RDV créé: {result['rdv_id']}",
                    metadata={"action": "create_rdv", "rdv_id": result["rdv_id"]}
                )

            return result["message"]

        except Exception as e:
            logger.error(f"Erreur handle_rdv_request: {e}")
            return "Erreur lors de la création du RDV. 😞"

    async def process_conversation(
        self,
        user_message: str,
        numero_client: str,
        chat_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Traite une conversation complète.
        Détecte les intentions et routage vers les bons outils.
        """
        # Contexte par défaut
        if context is None:
            context = {}

        # Détecter l'intention avec Claude
        intent_prompt = f"""
Quelle est l'intention du client ? Réponds avec UNIQUEMENT une de ces intentions:
- SEARCH (cherche un thérapeute)
- BOOK (veut agendar un RDV)
- QUESTION (pose une question générale)
- REGISTER (veut s'inscrire en tant que thérapeute)
- ESCALATE (demande à parler à quelqu'un)
- QUALIFY (contexte semble suspect)

Message: "{user_message}"

Réponds avec UNIQUEMENT l'intention, ex: SEARCH
"""

        response = await client.chat.complete_async(
            model="mistral-large-latest",
            max_tokens=10,
            messages=[UserMessage(content=intent_prompt)]
        )

        intent = response.choices[0].message.content.strip().upper()

        logger.info(f"Intent detected: {intent}")

        # Router vers le bon handler
        if intent == "SEARCH":
            return await self.handle_search_request(
                user_message, chat_history, numero_client
            )
        elif intent == "BOOK":
            # Demander les infos manquantes
            return (
                "✨ Pour agendar ton RDV, j'ai besoin de:\n"
                "1️⃣ Ton nom complet\n"
                "2️⃣ Ton email\n"
                "3️⃣ La date/heure souhaitée\n\n"
                "Partage ces infos et je confirmerai ton RDV !"
            )
        elif intent == "REGISTER":
            return (
                "💜 Bienvenue thérapeute !\n\n"
                "Pour créer votre profil sur Holisource:\n"
                "👉 https://holisource.com/inscription-therapeute\n\n"
                "Ou écrivez-moi pour plus d'infos !"
            )
        elif intent == "ESCALATE":
            return (
                "Je vais te mettre en relation avec notre équipe. 💜\n"
                "📧 contact@holisource.com\n"
                "☎️ +33 (à confirmer)\n\n"
                "Nous te répondrons rapidement !"
            )
        else:
            # QUESTION ou autre: répondre normalement avec Claude
            return await self.generate_response(
                user_message, chat_history, numero_client, context
            )


# Instance globale
_brain = None


def get_brain() -> HolisourceBrain:
    """Getter pour le brain (singleton)"""
    global _brain
    if _brain is None:
        _brain = HolisourceBrain()
    return _brain
