# agent/providers/__init__.py — Factory pour sélectionner le provider WhatsApp

import os
import logging
from agent.providers.base import ProveedorWhatsApp

logger = logging.getLogger("holisource_agent")


def obtener_proveedor() -> ProveedorWhatsApp:
    """
    Sélectionne et retourne le fournisseur WhatsApp configuré dans .env
    """
    proveedor = os.getenv("WHATSAPP_PROVIDER", "").lower()

    if not proveedor:
        raise ValueError(
            "WHATSAPP_PROVIDER non configuré en .env\n"
            "Utilise: meta ou twilio"
        )

    if proveedor == "meta":
        logger.info("Utilisant Meta Cloud API comme fournisseur WhatsApp")
        from agent.providers.meta import ProveedorMeta
        return ProveedorMeta()

    elif proveedor == "twilio":
        logger.info("Utilisant Twilio comme fournisseur WhatsApp")
        from agent.providers.twilio import ProveedorTwilio
        return ProveedorTwilio()

    else:
        raise ValueError(
            f"Fournisseur non supporté: {proveedor}\n"
            "Utilise: meta ou twilio"
        )
