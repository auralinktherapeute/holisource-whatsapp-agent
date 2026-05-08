# agent/providers/twilio.py — Adaptateur pour Twilio WhatsApp

import os
import base64
import logging
import httpx
from typing import List
from fastapi import Request

from agent.providers.base import ProveedorWhatsApp, MensajeEntrante

logger = logging.getLogger("holisource_agent")


class ProveedorTwilio(ProveedorWhatsApp):
    """Fournisseur WhatsApp utilisant Twilio"""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([self.account_sid, self.auth_token, self.phone_number]):
            logger.warning(
                "Credentials Twilio manquants "
                "(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)"
            )

    async def parsear_webhook(self, request: Request) -> List[MensajeEntrante]:
        """
        Parse le payload form-encoded de Twilio
        """
        try:
            form = await request.form()

            texto = form.get("Body", "")
            telefono = form.get("From", "").replace("whatsapp:", "")
            mensaje_id = form.get("MessageSid", "")

            if not texto:
                return []

            mensajes = [
                MensajeEntrante(
                    telefono=telefono,
                    texto=texto,
                    mensaje_id=mensaje_id,
                    es_propio=False,
                )
            ]

            logger.debug(f"Twilio: {len(mensajes)} mensaje(s) parseados")
            return mensajes

        except Exception as e:
            logger.error(f"Erreur parsear_webhook Twilio: {e}")
            return []

    async def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        """
        Envoie un message via Twilio API
        """
        try:
            if not all([self.account_sid, self.auth_token, self.phone_number]):
                logger.warning("Credentials Twilio manquants")
                return False

            url = (
                f"https://api.twilio.com/2010-04-01/Accounts/"
                f"{self.account_sid}/Messages.json"
            )

            # Authentification Basic (Account SID:Auth Token en base64)
            credentials = f"{self.account_sid}:{self.auth_token}"
            auth = base64.b64encode(credentials.encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}

            data = {
                "From": f"whatsapp:{self.phone_number}",
                "To": f"whatsapp:{telefono}",
                "Body": mensaje,
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, data=data, headers=headers, timeout=30.0
                )

                if response.status_code == 201:
                    logger.info(f"Message Twilio envoyé à {telefono}")
                    return True
                else:
                    logger.error(
                        f"Erreur Twilio API: {response.status_code} — {response.text}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Erreur enviar_mensaje Twilio: {e}")
            return False
