# Holisource WhatsApp Agent — Système d'Instructions pour Claude Code

> Ce fichier est le **CERVEAU** de l'Agent WhatsApp Holisource.
> Claude Code le lit automatiquement et sait exactement comment l'adapter
> à la plateforme Holisource (Supabase, Twilio, Resend, modération IA, etc.)

---

## 🎯 Vision du projet

**Holisource WhatsApp Agent** — Agent IA conversationnel pour l'annuaire de thérapeutes holistiques en Alsace.

L'agent répond directement via WhatsApp aux clients/patients qui cherchent un thérapeute, agende les rendez-vous, gère les leads et améliore l'expérience client.

**Spécificités par rapport à l'AgentKit standard :**
- ✅ Intégration **Supabase** complète (thérapeutes, rendez-vous, disponibilités, abonnements)
- ✅ Modération IA **Mistral** (refus des leads non qualifiés)
- ✅ Intégration **Calendly** (agenda thérapeutes)
- ✅ **SMS + Email** (confirmations via Resend + Twilio)
- ✅ **Gestion des abonnements** (Basic/Premium/Premium+)
- ✅ **Notifications in-app** (système Holisource)
- ✅ **Charte graphique Holisource** (respect des couleurs, tonalité)

---

## 🏗️ Architecture technique

### Stack Holisource
| Composant | Technologie | Usage |
|-----------|------------|-------|
| **IA** | Claude Sonnet 4.6 (+ Mistral pour modération) | Conversations, qualification leads |
| **WhatsApp** | Meta Cloud API / Twilio | Intégration messagerie |
| **Base de données** | Supabase PostgreSQL | Clients, rendez-vous, historique |
| **Email** | Resend | Confirmations, rappels |
| **SMS** | Twilio | Rappels, confirmations |
| **Calendrier** | Calendly API | Intégration agenda |
| **Serveur** | FastAPI + Uvicorn | Webhook handler |
| **Deploy** | Railway + Docker | Production |

### Connexion Supabase
- **Project ID** : `dqmujlqxpmcwscztrrdt`
- **Tables essentielles** :
  - `therapeutes` — Fiche du thérapeute
  - `rendez_vous` — Réservations clients
  - `disponibilites` — Créneaux libres
  - `chat_logs` — Historique conversations WhatsApp
  - `notifications` — Notifications in-app

---

## 📱 Flux principal

```
Client écrit sur WhatsApp
    ↓
Webhook Meta/Twilio → agent/providers/
    ↓
agent/main.py → agent/memory.py (historique Supabase)
    ↓
agent/brain.py → Claude Sonnet + system prompt Holisource
    ↓
agent/tools.py → Supabase + Calendly + Resend + Twilio
    ↓
Réponse WhatsApp + actions (email, SMS, créer lead, etc.)
    ↓
Client reçoit la réponse
```

---

## 🎨 Charte graphique Holisource dans WhatsApp

**Tonalité** : Empathique, professionnel, chaleureux
- Salutations personnalisées
- Respect de la langue française
- Emojis limités (💜 violet Holisource, ✨)
- Format clair : numérotation, retours à la ligne

**Exemple de message :**
```
Bonjour ! 💜

Je suis Sofia, l'assistante virtuelle de Holisource.
Bienvenue dans notre annuaire de thérapeutes holistiques en Alsace.

Comment puis-je t'aider ?
1️⃣ Trouver un thérapeute
2️⃣ Agendar un rendez-vous
3️⃣ Poser une question
```

---

## 🔄 Flux d'onboarding — 5 phases

### PHASE 1 — Vérification environnement

**Vérifications :**
1. Python >= 3.11
2. Créer dossiers : `agent/`, `config/`, `knowledge/`, `tests/`
3. Dépendances Python (voir section Stack)
4. Variables `.env` (Anthropic, Supabase, Twilio, Meta, Resend, Calendly)

### PHASE 2 — Configuration Holisource

Poser ces questions UNE PAR UNE (adapter à Holisource, pas besoin de refaire entrevista du negocio) :

```
QUESTION 1: En quel nom souhaitez-vous déployer cet agent ?
            (Ex: "Sofia - Holisource" ou "Assistant Holisource")

QUESTION 2: Quel est votre Anthropic API Key ?

QUESTION 3: Avez-vous une API Key Resend ?
            (Pour confirmations email via Resend)

QUESTION 4: Avez-vous un compte Twilio pour les SMS ?
            (Account SID, Auth Token, Phone Number)

QUESTION 5: Quel serveur WhatsApp voulez-vous utiliser ?
            1. Meta Cloud API (officiel, recommandé)
            2. Twilio (sandbox gratuit pour tester)

QUESTION 6: Voulez-vous intégrer avec Calendly ?
            (Calendly API key si oui)

QUESTION 7: Avez-vous une API Key Mistral pour modération ?
            (Pour filtrer les leads non qualifiés)
```

### PHASE 3 — Génération du code

Générer :
1. **config/holisource_config.yaml** — Données spécifiques Holisource
2. **config/prompts_holisource.yaml** — System prompt adapté
3. **agent/supabase_client.py** — Client Supabase async
4. **agent/holisource_tools.py** — Outils Holisource (recherche thérapeute, agendar, qualifier lead, etc.)
5. **agent/providers/** — Meta + Twilio (adapter de l'AgentKit)
6. **agent/main.py** — FastAPI server Holisource
7. **agent/brain.py** — Claude API + Mistral modération
8. **agent/memory.py** — SQLAlchemy + Supabase chat_logs
9. **tests/test_local_holisource.py** — Test terminal
10. **requirements.txt** — Dépendances (fastapi, supabase, anthropic, etc.)

### PHASE 4 — Test local

1. `python tests/test_local_holisource.py`
2. Simuler conversations (recherche thérapeute, agendar RDV, questions générales)
3. Ajuster system prompt si besoin

### PHASE 5 — Deploy Railway

1. Build Docker
2. GitHub push
3. Connecter Railway
4. Configurer webhook WhatsApp (Meta ou Twilio)

---

## 🔧 Fichiers à générer — Détails

### 1. `config/holisource_config.yaml`

```yaml
# Configuration spécifique Holisource
holisource:
  nom_agent: "Sofia"
  slogan: "Votre assistante pour trouver le bon thérapeute holistique"
  departements: ["67", "68"]  # Alsace
  region: "Alsace"
  
supabase:
  project_id: "dqmujlqxpmcwscztrrdt"
  # URL + anon key depuis .env
  
intégrations:
  calendly: true
  resend: true
  twilio: true
  mistral_moderation: true

metadata:
  version: "1.0"
  creé: "2026-05-08"
```

### 2. `config/prompts_holisource.yaml`

```yaml
system_prompt: |
  Tu es Sofia, l'assistante virtuelle de Holisource.
  
  ## Identité
  - Nom: Sofia
  - Plateforme: Holisource — Annuaire de thérapeutes holistiques en Alsace
  - Région: Alsace (Bas-Rhin 67 + Haut-Rhin 68)
  - Tonalité: Empathique, professionnel, chaleureux
  
  ## Missions principales
  1. **Aider les patients à trouver un thérapeute** 
     - Spécialité recherchée
     - Localisation (ville, code postal)
     - Modalité (présentiel, distanciel, les deux)
     - Budget
  
  2. **Agendar les rendez-vous**
     - Intégration Calendly des thérapeutes
     - Confirmation email + SMS
     - Rappel 24h avant
  
  3. **Qualifier les leads**
     - Questions pour comprendre les besoins
     - Évaluer si le patient est qualifié (sincère, engagé, budget ok)
     - Escalade aux vendeurs si needed
  
  4. **Répondre aux questions générales**
     - Qu'est-ce que l'holisitique ?
     - Quelles spécialités y a-t-il ?
     - Comment ça marche ?
  
  ## Données Holisource (depuis Supabase)
  [DYNAMIQUE - lue depuis la base de données]
  
  ## Règles
  - TOUJOURS en français
  - JAMAIS inventer de thérapeute
  - JAMAIS partager les emails directs des thérapeutes
  - Demander consentement avant d'agendar
  - Offrir "Créer un profil Holisource" aux nouveaux thérapeutes
  
  ## Horaires
  Disponible 24/7 (agent automatisé)
  
  fallback_message: "Désolée, je n'ai pas bien compris. Pourrais-tu reformuler ?"
  error_message: "Oups ! J'ai un souci technique. Réessaye dans quelques instants."
```

### 3. `agent/supabase_client.py`

```python
# Client Supabase pour l'agent WhatsApp
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def search_therapeutes(self, filters: dict) -> list:
        """
        Cherche des thérapeutes selon les critères
        filters: { specialite, ville, modalite, tarif_max, etc. }
        """
        query = self.supabase.table("therapeutes") \
            .select("id,nom,prenom,specialites,ville,modalite,description,tarif_min,tarif_max,calendly_url,rating") \
            .eq("statut", "approved")
        
        if "specialite" in filters:
            query = query.contains("specialites", [filters["specialite"]])
        if "ville" in filters:
            query = query.ilike("ville", f"%{filters['ville']}%")
        if "modalite" in filters:
            query = query.eq("modalite", filters["modalite"])
        
        result = query.execute()
        return result.data if result.data else []
    
    async def get_therapeute(self, therapeute_id: str) -> dict:
        """Récupère le profil complet d'un thérapeute"""
        result = self.supabase.table("therapeutes") \
            .select("*") \
            .eq("id", therapeute_id) \
            .single() \
            .execute()
        return result.data
    
    async def create_rdv(self, data: dict):
        """Crée un rendez-vous"""
        result = self.supabase.table("rendez_vous").insert(data).execute()
        return result.data
    
    async def log_chat(self, telefono: str, role: str, message: str):
        """Log la conversation dans chat_logs"""
        self.supabase.table("chat_logs").insert({
            "numero_client": telefono,
            "role": role,
            "message": message,
            "timestamp": "now()"
        }).execute()
```

### 4. `agent/holisource_tools.py`

Outils spécifiques :
```python
# Fonctions principales
- search_therapeutes(specialite, ville, modalite, budget)
- get_therapeute_details(id)
- check_disponibilites_calendly(therapeute_id)
- create_rdv(client_name, client_phone, therapeute_id, slot)
- qualify_lead(contexte_conversation) -> Mistral moderation
- send_confirmation_email(client_email, rdv_data) -> Resend
- send_confirmation_sms(client_phone, rdv_data) -> Twilio
- notify_therapeute(therapeute_id, new_client) -> Supabase notifications
```

### 5. `agent/main.py`

FastAPI server standard (adapter de l'AgentKit) + routes spécifiques Holisource

### 6. `agent/brain.py`

Claude API + Mistral pour qualification leads

### 7. `agent/memory.py`

SQLAlchemy + Supabase chat_logs (adapter de l'AgentKit)

### 8. `tests/test_local_holisource.py`

Terminal chat simulator

### 9. `requirements.txt`

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
anthropic>=0.40.0
httpx>=0.25.0
python-dotenv>=1.0.0
sqlalchemy>=2.0.0
pyyaml>=6.0.1
aiosqlite>=0.19.0
python-multipart>=0.0.6
supabase>=2.0.0
resend>=0.5.0
twilio>=8.0.0
```

### 10. `.env.example`

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGc...

# WhatsApp Provider
WHATSAPP_PROVIDER=meta  # ou twilio

# Meta Cloud API
META_ACCESS_TOKEN=...
META_PHONE_NUMBER_ID=...
META_VERIFY_TOKEN=holisource-verify

# Twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=whatsapp:+...

# Resend (emails)
RESEND_API_KEY=re_...

# Calendly
CALENDLY_API_KEY=...

# Mistral (modération leads)
MISTRAL_API_KEY=...

# Serveur
PORT=8000
ENVIRONMENT=development
```

---

## 📋 Règles de comportement

1. **Français partout** — messages, code, commentaires
2. **UNE question à la fois** — ne pas bombarder
3. **Variables d'environnement** — JAMAIS hardcoder les secrets
4. **Test local d'abord** — avant deploy
5. **Erreurs claires** — diagnostic + solution
6. **Code commenté en français** — que l'utilisateur comprenne
7. **Validations à chaque phase** — avant d'avancer

---

## 🚀 Commandes utiles

```bash
# Test local
python tests/test_local_holisource.py

# Lancer le serveur
uvicorn agent.main:app --reload --port 8000

# Docker
docker compose up --build

# Logs
docker compose logs -f agent
```

---

## 📱 Cas d'usage Holisource

1. **Recherche thérapeute** → Filtrer par spécialité, localité, modalité
2. **Agendar RDV** → Via Calendly, confirmation email/SMS
3. **Questions générales** → Qu'est-ce que holistique, spécialités disponibles, etc.
4. **Création de compte thérapeute** → "Vous êtes thérapeute? Créez votre profil"
5. **Escalade** → "Je vais te connecter avec notre équipe" → notification Slack/in-app

---

## 🔐 Sécurité

- RLS Supabase actif
- Pas de tokens dans les messages WhatsApp
- WEBHOOK_SECRET pour validation
- Validation des inputs
- Rate limiting sur les recherches

---

**Version** : 1.0  
**Créé** : 2026-05-08  
**Adapté pour** : Holisource.com
