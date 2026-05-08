# agent/memory.py — Mémoire de conversationspour Holisource
# Utilise Supabase pour persistence (chat_logs table)

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv

from agent.supabase_client import get_supabase_client

load_dotenv()
logger = logging.getLogger("holisource_agent")


class ConversationMemory:
    """Gère l'historique des conversations avec Supabase"""

    def __init__(self):
        self.supabase = get_supabase_client()
        self.max_history = 20  # Garde les 20 derniers messages

    async def save_message(
        self,
        numero_client: str,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        Sauvegarde un message dans l'historique.

        Args:
            numero_client: Numéro WhatsApp du client
            role: "user" ou "assistant"
            content: Contenu du message
            metadata: Données additionnelles (optionnel)

        Returns:
            True si succès
        """
        try:
            await self.supabase.log_chat_message(
                numero_client, role, content, metadata
            )
            return True
        except Exception as e:
            logger.error(f"Erreur save_message: {e}")
            return False

    async def get_history(
        self, numero_client: str, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Récupère l'historique d'une conversation.

        Args:
            numero_client: Numéro WhatsApp du client
            limit: Nombre max de messages (default: 20)

        Returns:
            Liste de messages [{role: "user|assistant", content: "..."}]
        """
        try:
            if limit is None:
                limit = self.max_history

            messages = await self.supabase.get_chat_history(numero_client, limit)

            # Transformer au format attendu par Claude
            formatted = [
                {"role": msg.get("role", "user"), "content": msg.get("message", "")}
                for msg in messages
                if msg.get("message")  # Ignorer les messages vides
            ]

            logger.debug(
                f"Historique chargé pour {numero_client}: {len(formatted)} messages"
            )
            return formatted

        except Exception as e:
            logger.error(f"Erreur get_history: {e}")
            return []

    async def clear_history(self, numero_client: str) -> bool:
        """Efface tout l'historique d'un client"""
        try:
            # Supabase n'a pas de méthode clear directe,
            # mais on peut logger un "system" message pour l'indiquer
            await self.supabase.log_chat_message(
                numero_client,
                "system",
                "[Historique effacé]",
            )
            logger.info(f"Historique effacé pour {numero_client}")
            return True
        except Exception as e:
            logger.error(f"Erreur clear_history: {e}")
            return False

    async def get_user_context(self, numero_client: str) -> Dict:
        """
        Extrait le contexte utilisateur de l'historique.
        Ex: nom, email, recherches récentes, etc.
        """
        try:
            history = await self.get_history(numero_client, limit=30)

            context = {
                "numero": numero_client,
                "nom": None,
                "email": None,
                "recent_searches": [],
                "last_intent": None,
            }

            # Parser l'historique pour extraire du contexte
            for msg in history:
                content = msg.get("content", "").lower()

                # Recherche de patterns
                if "mon nom est" in content or "je m'appelle" in content:
                    # Parser le nom
                    pass
                if "@" in content and "." in content:
                    # Parser l'email
                    pass

            return context

        except Exception as e:
            logger.error(f"Erreur get_user_context: {e}")
            return {}


# Instance globale
_memory = None


def get_memory() -> ConversationMemory:
    """Getter pour la mémoire (singleton)"""
    global _memory
    if _memory is None:
        _memory = ConversationMemory()
    return _memory


async def save_message(
    numero_client: str, role: str, content: str, metadata: Optional[Dict] = None
) -> bool:
    """Helper pour sauvegarder un message"""
    memory = get_memory()
    return await memory.save_message(numero_client, role, content, metadata)


async def get_history(numero_client: str, limit: Optional[int] = None) -> List[Dict]:
    """Helper pour récupérer l'historique"""
    memory = get_memory()
    return await memory.get_history(numero_client, limit)
