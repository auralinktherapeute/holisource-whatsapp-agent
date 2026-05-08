# agent/providers/base.py — Classe abstraite pour provid WhatsApp
# Adapter pattern pour Meta Cloud API et Twilio

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from fastapi import Request


@dataclass
class MensajeEntrante:
    """Message normalisé — même format peu importe le fournisseur"""

    telefono: str  # Numéro du remitent
    texto: str  # Contenu du message
    mensaje_id: str  # ID unique du message
    es_propio: bool  # True si envoyé par l'agent (on ignore)


class ProveedorWhatsApp(ABC):
    """Interface commune pour tous les fournisseurs WhatsApp"""

    @abstractmethod
    async def parsear_webhook(self, request: Request) -> List[MensajeEntrante]:
        """Extrait et normalise les messages du webhook"""
        ...

    @abstractmethod
    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        """Envoie un message. Retourne True si succès"""
        ...

    async def validar_webhook(self, request: Request) -> Optional[int]:
        """Vérification GET du webhook (seulement Meta). Retourne None si non applicable"""
        return None
