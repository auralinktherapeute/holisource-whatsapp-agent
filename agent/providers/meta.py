# agent/providers/meta.py — Adaptateur pour Meta Cloud API WhatsApp

import os
import logging
import httpx
from typing import List, Optional
from fastapi import Request

from agent.providers.base import ProveedorWhatsApp, MensajeEntrante

logger = logging.getLogger("holisource_agent")


class ProveedorMeta(ProveedorWhatsApp):
    """Fournisseur WhatsApp utilisant Meta Cloud API (officiel)"""

    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("META_PHONE_NUMBER_ID")
        self.verify_token = os.getenv("META_VERIFY_TOKEN", "holisource-verify")
        self.api_version = "v21.0"

        if not self.access_token or not self.phone_number_id:
            logger.warning(
                "META_ACCESS_TOKEN ou META_PHONE_NUMBER_ID manquent"
            )

    async def validar_webhook(self, request: Request) -> Optional[int]:
        """
        Meta requiert une vérification GET avec hub.verify_token
        """
        try:
            params = request.query_params
            mode = params.get("hub.mode")
            token = params.get("hub.verify_token")
            challenge = params.get("hub.challenge")

            if mode == "subscribe" and token == self.verify_token:
                logger.info("Webhook Meta vérifié avec succès")
                return int(challenge)

            logger.warning("Webhook Meta: token invalide")
            return None

        except Exception as e:
            logger.error(f"Erreur validar_webhook Meta: {e}")
            return None

    async def parsear_webhook(self, request: Request) -> List[MensajeEntrante]:
        """
        Parse le payload anidé de Meta Cloud API
        """
        try:
            body = await request.json()
            mensajes = []

            # Structure Meta: entry[] > changes[] > value > messages[]
            for entry in body.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})

                    # Messages entrants
                    for msg in value.get("messages", []):
                        if msg.get("type") == "text":
                            mensajes.append(
                                MensajeEntrante(
                                    telefono=msg.get("from", ""),
                                    texto=msg.get("text", {}).get("body", ""),
                                    mensaje_id=msg.get("id", ""),
                                    es_propio=False,
                                )
                            )

            logger.debug(f"Meta: {len(mensajes)} mensaje(s) parseados")
            return mensajes

        except Exception as e:
            logger.error(f"Erreur parsear_webhook Meta: {e}")
            return []

    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        """
        Envoie un message via Meta Cloud API
        """
        try:
            if not self.access_token or not self.phone_number_id:
                logger.warning("Credentials Meta manquants")
                return False

            url = (
                f"https://graph.facebook.com/{self.api_version}/"
                f"{self.phone_number_id}/messages"
            )

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": telefono,
                "type": "text",
                "text": {"body": mensaje},
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=payload, headers=headers, timeout=30.0
                )

                if response.status_code == 200:
                    logger.info(f"Message envoyé à {telefono}")
                    return True
                else:
                    logger.error(
                        f"Erreur Meta API: {response.status_code} — {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Erreur enviar_mensaje Meta: {e}")
            return False
