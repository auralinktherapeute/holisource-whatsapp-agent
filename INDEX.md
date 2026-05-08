# 📑 Index Holisource WhatsApp Agent

Structure complète et guide de navigation du projet.

---

## 📂 Structure du projet

```
holisource-whatsapp-agent/
├── 📄 CLAUDE.md                  ← Instructions pour Claude Code
├── 📄 README.md                  ← Vue d'ensemble du projet
├── 📄 SETUP.md                   ← Guide de mise en place complet
├── 📄 INDEX.md                   ← Ce fichier
├── 📄 .gitignore                 ← Fichiers à ignorer en git
├── 📄 .env.example               ← Template des variables d'environnement
├── 📄 requirements.txt           ← Dépendances Python
├── 📄 Dockerfile                 ← Image Docker pour production
├── 📄 docker-compose.yml         ← Orchestration Docker
│
├── 📁 agent/                     ← Cœur de l'application
│   ├── __init__.py
│   ├── main.py                   ← FastAPI server + webhook handler
│   ├── brain.py                  ← Claude AI + routage des intentions
│   ├── memory.py                 ← Persistance des conversations (Supabase)
│   ├── supabase_client.py        ← Client Supabase async
│   ├── holisource_tools.py       ← Outils métier (recherche, RDV, etc.)
│   └── providers/
│       ├── __init__.py           ← Factory de sélection du provider
│       ├── base.py               ← Classe abstraite ProveedorWhatsApp
│       ├── meta.py               ← Adaptateur Meta Cloud API
│       └── twilio.py             ← Adaptateur Twilio
│
├── 📁 config/                    ← Configuration Holisource
│   ├── holisource_config.yaml    ← Configuration globale (régions, spécialités, etc.)
│   └── prompts_holisource.yaml   ← System prompt pour Sofia
│
├── 📁 knowledge/                 ← Fichiers de connaissance (FAQ, menu, etc.)
│   └── .gitkeep                  ← Placeholder
│
└── 📁 tests/                     ← Tests
    ├── __init__.py
    └── test_local.py             ← Chat local pour tester l'agent
```

---

## 🎯 Fichiers clés par fonction

### 🚀 Démarrage & Configuration

| Fichier | Purpose | Actions |
|---------|---------|---------|
| `SETUP.md` | Guide de mise en place step-by-step | **Lis ça d'abord** |
| `.env.example` | Template des secrets | `cp .env.example .env` puis remplis |
| `requirements.txt` | Dépendances Python | `pip install -r requirements.txt` |
| `CLAUDE.md` | Instructions pour Claude Code | Instructions système |

### 🧠 Application principale

| Fichier | Purpose | Clé: |
|---------|---------|------|
| `agent/main.py` | Serveur FastAPI + webhooks | `@app.post("/webhook")` |
| `agent/brain.py` | Claude AI + intent routing | `async def process_conversation()` |
| `agent/holisource_tools.py` | Logique métier Holisource | Recherche, RDV, qualification |
| `agent/memory.py` | Historique des conversations | `get_history()`, `save_message()` |
| `agent/supabase_client.py` | Accès à la DB Supabase | `search_therapeutes()`, `create_rdv()` |

### 📱 Intégration WhatsApp

| Fichier | Purpose | Utilisé par |
|---------|---------|-----------|
| `agent/providers/base.py` | Interface commune | Tous les providers |
| `agent/providers/meta.py` | Meta Cloud API | Si `WHATSAPP_PROVIDER=meta` |
| `agent/providers/twilio.py` | Twilio | Si `WHATSAPP_PROVIDER=twilio` |
| `agent/providers/__init__.py` | Factory de sélection | `obtener_proveedor()` |

### ⚙️ Configuration

| Fichier | Purpose | Utilisation |
|---------|---------|-------------|
| `config/holisource_config.yaml` | Config globale Holisource | Régions, spécialités, intégrations |
| `config/prompts_holisource.yaml` | System prompt pour Sofia | Chargé par `agent/brain.py` |

### 🧪 Tests & Debug

| Fichier | Purpose | Commande |
|---------|---------|----------|
| `tests/test_local.py` | Chat local dans le terminal | `python tests/test_local.py` |

### 📦 Déploiement

| Fichier | Purpose | Utilisation |
|---------|---------|-------------|
| `Dockerfile` | Image Docker pour prod | `docker build -t ...` |
| `docker-compose.yml` | Orchestration Docker | `docker compose up` |

---

## 🔄 Flux d'exécution principal

```
Webhook WhatsApp (Meta/Twilio)
    ↓
agent/main.py:webhook_handler()
    ↓
agent/providers/meta.py ou twilio.py
    ↓ (normalise le message)
agent/brain.py:process_conversation()
    ↓ (détecte l'intention avec Claude)
    ├─ SEARCH → agent/holisource_tools.py:search_therapeutes()
    ├─ BOOK → agent/holisource_tools.py:create_rdv_with_confirmation()
    ├─ QUESTION → agent/brain.py:generate_response()
    ├─ REGISTER → propose inscription
    └─ ESCALATE → propose escalade
    ↓
agent/memory.py:save_message() (sauvegarde dans Supabase chat_logs)
    ↓
Réponse envoyée via Meta/Twilio
```

---

## 🔑 Concepts clés

### Intents (Intentions détectées par Claude)

- **SEARCH** — Client cherche un thérapeute
- **BOOK** — Client veut agendar un RDV
- **QUESTION** — Question générale
- **REGISTER** — Veut s'inscrire comme thérapeute
- **ESCALATE** — Veut parler à un humain
- **QUALIFY** — Lead à analyser

### Providers (Fournisseurs WhatsApp)

Deux options avec le même code:

- **Meta Cloud API** — Officiel WhatsApp, production prête
- **Twilio** — Sandbox gratuit pour tester rapidement

Adapter pattern: chaque provider implémente `ProveedorWhatsApp` avec:
- `parsear_webhook()` — Normalise le format du message
- `enviar_mensaje()` — Envoie une réponse
- `validar_webhook()` — Vérification GET (Meta seulement)

### Tools (Outils métier)

Fonctions spécifiques à Holisource:

```python
search_therapeutes()              # Cherche dans Supabase
get_therapeute_details()          # Détails d'un thérapeute
create_rdv_with_confirmation()    # Agende + email + SMS
qualify_lead()                    # Mistral AI modération
create_lead()                     # Crée un prospect
```

---

## 🚀 Commandes courantes

### Développement

```bash
# Cloner le projet
cd /Users/geraldhenry/claude/holisource-whatsapp-agent

# Configurer .env
cp .env.example .env
# Édite .env et ajoute les clés API

# Installer dépendances
pip install -r requirements.txt

# Test local (chat dans le terminal)
python tests/test_local.py

# Lancer le serveur FastAPI
uvicorn agent.main:app --reload --port 8000

# Health check
curl http://localhost:8000/health
```

### Docker (Production)

```bash
# Build
docker compose build

# Lancer
docker compose up

# Arrêter
docker compose down

# Logs
docker compose logs -f agent
```

### Git & GitHub

```bash
# Committer
git add .
git commit -m "feat: ..."
git push

# Créer un repo
git init
git remote add origin https://github.com/USER/holisource-whatsapp-agent.git
git push -u origin main
```

---

## 📊 Dépendances externes

### APIs utilisées

| Service | Utilisé pour | Fichier |
|---------|-------------|---------|
| **Anthropic Claude** | IA conversationnelle | `agent/brain.py` |
| **Supabase** | Base de données | `agent/supabase_client.py` |
| **Meta Cloud API** | WhatsApp (officiel) | `agent/providers/meta.py` |
| **Twilio** | WhatsApp (alternative) | `agent/providers/twilio.py` |
| **Resend** | Emails transactionnels | `agent/holisource_tools.py` |
| **Mistral** | Modération de leads (optionnel) | `agent/holisource_tools.py` |

### Python packages

| Package | Version | Usage |
|---------|---------|-------|
| `fastapi` | ≥0.104.0 | Framework web |
| `uvicorn` | ≥0.24.0 | Serveur ASGI |
| `anthropic` | ≥0.40.0 | Claude API client |
| `supabase` | ≥2.0.0 | Supabase client |
| `httpx` | ≥0.25.0 | HTTP async |
| `pyyaml` | ≥6.0.1 | Parsing YAML |
| `python-dotenv` | ≥1.0.0 | Variables d'environnement |
| `twilio` | ≥8.0.0 | Twilio client |
| `resend` | ≥0.5.0 | Resend client |

---

## 🎯 Points d'entrée du code

### Si tu veux comprendre...

| Concept | Lis d'abord |
|---------|-----------|
| Comment ça marche globalement | `README.md` + `CLAUDE.md` |
| Configurer l'agent | `SETUP.md` |
| Structure du code | Ce fichier (INDEX.md) |
| Créer un thérapeute | `agent/holisource_tools.py` line ~search_therapeutes |
| Agendar un RDV | `agent/holisource_tools.py` line ~create_rdv_with_confirmation |
| Gérer la conversation | `agent/brain.py` line ~process_conversation |
| Sauvegarder l'historique | `agent/memory.py` |
| Intégrer un nouveau provider | `agent/providers/base.py` |

---

## 🔐 Sécurité

**Secrets à protéger:**
- `ANTHROPIC_API_KEY` — Copier depuis `.env.example`, jamais versionner `.env`
- `SUPABASE_KEY` — Supabase RLS protège les données
- `META_ACCESS_TOKEN` — Token Meta WhatsApp
- `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` — Credentials Twilio

**Protection:**
- `.env` dans `.gitignore` — jamais committer
- RLS Supabase actif sur toutes les tables
- Validate webhook avec `VERIFY_TOKEN`

---

## 📈 Prochaines améliorations

- [ ] Intégrer Calendly API pour auto-sync des disponibilités
- [ ] Dashboard admin pour monitorer les conversations
- [ ] Escalade automatique aux vendeurs via API
- [ ] Analytics & metrics sur les intentions détectées
- [ ] Multi-langue support
- [ ] Rabot de feedback post-RDV
- [ ] Intégration SMS rappels 24h avant RDV

---

## 📞 Support

- **Documentation**: `README.md`, `SETUP.md`
- **Code**: Cherche les docstrings dans `agent/*.py`
- **Issues**: GitHub Issues ou `contact@holisource.com`

---

**Créé**: 2026-05-08  
**Version**: 1.0  
**Pour**: Holisource.com
