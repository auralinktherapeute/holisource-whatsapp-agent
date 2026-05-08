# agent/supabase_client.py — Client Supabase async pour Holisource
# Intégration avec la base de données Holisource

import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except ImportError:
    raise ImportError("supabase non installé. Installe avec: pip install supabase")

load_dotenv()
logger = logging.getLogger("holisource_agent")


class HolisourceSupabaseClient:
    """Client Supabase pour l'agent WhatsApp Holisource"""

    def __init__(self):
        """Initialise la connexion Supabase"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL et SUPABASE_KEY manquent dans .env"
            )

        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Client Supabase connecté")

    # ════════════════════════════════════════════════════════════
    # RECHERCHE THÉRAPEUTES
    # ════════════════════════════════════════════════════════════

    async def search_therapeutes(
        self,
        specialite: Optional[str] = None,
        ville: Optional[str] = None,
        modalite: Optional[str] = None,
        tarif_max: Optional[int] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Cherche des thérapeutes selon les critères du client.

        Args:
            specialite: Spécialité recherchée (ex: "reiki")
            ville: Localité (ex: "Strasbourg")
            modalite: "presentiel" | "distanciel" | "les_deux"
            tarif_max: Budget maximum (ex: 100)
            limit: Nombre max de résultats

        Returns:
            Liste de thérapeutes matching
        """
        try:
            query = (
                self.supabase.table("therapeutes")
                .select(
                    "id,nom,prenom,specialites,ville,code_postal,"
                    "modalite,description,tarif_min,tarif_max,"
                    "calendly_url,is_featured,profile_completion"
                )
                .eq("statut", "approved")  # Seulement les approuvés
                .limit(limit)
            )

            # Filtres optionnels
            if specialite:
                # specialites est un array JSON, cherche si le specialite y est
                query = query.contains("specialites", f'["{specialite}"]')

            if ville:
                query = query.ilike("ville", f"%{ville}%")

            if modalite and modalite in ["presentiel", "distanciel", "les_deux"]:
                query = query.eq("modalite", modalite)

            if tarif_max:
                # tarif_min du thérapeute doit être <= tarif_max du client
                query = query.lte("tarif_min", tarif_max)

            result = query.execute()
            logger.info(
                f"Recherche thérapeute: {len(result.data or [])} résultats"
            )
            return result.data or []

        except Exception as e:
            logger.error(f"Erreur recherche thérapeutes: {e}")
            return []

    async def get_therapeute(self, therapeute_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le profil complet d'un thérapeute"""
        try:
            result = (
                self.supabase.table("therapeutes")
                .select("*")
                .eq("id", therapeute_id)
                .eq("statut", "approved")
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur get_therapeute: {e}")
            return None

    # ════════════════════════════════════════════════════════════
    # RENDEZ-VOUS
    # ════════════════════════════════════════════════════════════

    async def create_rdv(self, rdv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crée un rendez-vous dans Supabase.

        Données attendues:
        {
            "therapeute_id": "uuid",
            "client_nom": "Jean Dupont",
            "client_email": "jean@example.com",
            "client_telephone": "+33612345678",
            "date_rdv": "2026-05-15T14:00:00",
            "raison": "Séance de reiki",
            "modalite": "presentiel",
            "statut": "confirmed",  # confirmed, cancelled, completed
        }
        """
        try:
            result = self.supabase.table("rendez_vous").insert(rdv_data).execute()
            logger.info(f"RDV créé: {result.data[0]['id'] if result.data else 'erreur'}")
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erreur create_rdv: {e}")
            return None

    async def get_rdv(self, rdv_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un rendez-vous"""
        try:
            result = (
                self.supabase.table("rendez_vous")
                .select("*")
                .eq("id", rdv_id)
                .single()
                .execute()
            )
            return result.data
        except Exception as e:
            logger.error(f"Erreur get_rdv: {e}")
            return None

    async def list_rdv_by_therapeute(
        self, therapeute_id: str
    ) -> List[Dict[str, Any]]:
        """Liste tous les RDV d'un thérapeute"""
        try:
            result = (
                self.supabase.table("rendez_vous")
                .select("*")
                .eq("therapeute_id", therapeute_id)
                .order("date_rdv", desc=False)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Erreur list_rdv_by_therapeute: {e}")
            return []

    # ════════════════════════════════════════════════════════════
    # DISPONIBILITÉS
    # ════════════════════════════════════════════════════════════

    async def get_disponibilites(
        self, therapeute_id: str
    ) -> List[Dict[str, Any]]:
        """Récupère les créneaux libres d'un thérapeute"""
        try:
            result = (
                self.supabase.table("disponibilites")
                .select("*")
                .eq("therapeute_id", therapeute_id)
                .eq("is_booked", False)
                .order("date_heure", desc=False)
                .execute()
            )
            return result.data or []
        except Exception as e:
            logger.error(f"Erreur get_disponibilites: {e}")
            return []

    # ════════════════════════════════════════════════════════════
    # CHAT LOGS
    # ════════════════════════════════════════════════════════════

    async def log_chat_message(
        self,
        numero_client: str,
        role: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Log une conversation WhatsApp dans chat_logs.
        (Logging désactivé temporairement — schéma à normaliser)
        """
        try:
            # Logging temporairement désactivé pour éviter les erreurs de schéma
            # TODO: Normaliser le schéma chat_logs et réactiver
            logger.debug(f"[LOGGING DISABLED] {role}: {message[:50]}...")
            return True
        except Exception as e:
            logger.debug(f"Log skipped: {str(e)[:50]}")
            return True

    async def get_chat_history(
        self, numero_client: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Récupère l'historique de chat d'une session (désactivé temporairement)"""
        # Historique désactivé — schéma à normaliser
        # Pour l'instant, retourne un historique vide
        return []

    # ════════════════════════════════════════════════════════════
    # NOTIFICATIONS
    # ════════════════════════════════════════════════════════════

    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        type: str = "info",
    ) -> bool:
        """
        Crée une notification in-app Holisource.

        Types: "info", "warning", "success", "error"
        """
        try:
            self.supabase.table("notifications").insert(
                {
                    "user_id": user_id,
                    "title": title,
                    "message": message,
                    "type": type,
                    "is_read": False,
                    "created_at": datetime.utcnow().isoformat(),
                }
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Erreur create_notification: {e}")
            return False

    # ════════════════════════════════════════════════════════════
    # AVIS / FEEDBACK
    # ════════════════════════════════════════════════════════════

    async def create_avis(self, avis_data: Dict[str, Any]) -> bool:
        """
        Crée un avis client après un RDV.

        Données:
        {
            "therapeute_id": "uuid",
            "client_nom": "Jean Dupont",
            "client_email": "jean@example.com",
            "rdv_id": "uuid",
            "rating": 5,  # 1-5
            "commentaire": "Excellente séance !",
            "date_avis": "2026-05-16",
        }
        """
        try:
            self.supabase.table("avis").insert(avis_data).execute()
            logger.info(f"Avis créé pour thérapeute {avis_data.get('therapeute_id')}")
            return True
        except Exception as e:
            logger.error(f"Erreur create_avis: {e}")
            return False

    # ════════════════════════════════════════════════════════════
    # LEADS / PROSPECTS
    # ════════════════════════════════════════════════════════════

    async def create_lead(self, lead_data: Dict[str, Any]) -> Optional[str]:
        """
        Crée un lead/prospect depuis une conversation WhatsApp.

        Données:
        {
            "numero_whatsapp": "+33612345678",
            "nom": "Jean Dupont",
            "email": "jean@example.com",
            "specialite_recherchee": "reiki",
            "localisation": "Strasbourg",
            "budget": "50",
            "source": "whatsapp",
            "status": "new",  # new, contacted, interested, converted, rejected
            "notes": "Cherche reiki à Strasbourg, budget 50€/séance",
            "created_at": datetime.utcnow().isoformat(),
        }
        """
        try:
            result = self.supabase.table("prospects").insert(lead_data).execute()
            lead_id = result.data[0]["id"] if result.data else None
            logger.info(f"Lead créé: {lead_id}")
            return lead_id
        except Exception as e:
            logger.error(f"Erreur create_lead: {e}")
            return None

    # ════════════════════════════════════════════════════════════
    # UTILITAIRES
    # ════════════════════════════════════════════════════════════

    async def health_check(self) -> bool:
        """Teste la connexion Supabase"""
        try:
            self.supabase.table("therapeutes").select("id").limit(1).execute()
            logger.info("Supabase health check: OK")
            return True
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False


# Instance globale
_client = None


def get_supabase_client() -> HolisourceSupabaseClient:
    """Getter pour la client Supabase (singleton)"""
    global _client
    if _client is None:
        _client = HolisourceSupabaseClient()
    return _client
