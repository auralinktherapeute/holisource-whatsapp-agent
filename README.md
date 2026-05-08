# 🧘 Holisource WhatsApp Agent

Agent IA conversationnel pour l'annuaire de thérapeutes holistiques en Alsace.

**Sofia** répond directement sur WhatsApp pour aider les clients à trouver un thérapeute, agendar des rendez-vous, et qualifier les leads.

---

## 🚀 Démarrage rapide

### 1. Cloner & Configurer

```bash
cd /Users/geraldhenry/claude/holisource-whatsapp-agent
cp .env.example .env
```

### 2. Remplir le `.env`

Ajoute tes clés API dans `.env`:

```env
MISTRAL_API_KEY=...
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGc...
WHATSAPP_PROVIDER=meta  # ou twilio
META_ACCESS_TOKEN=...
RESEND_API_KEY=...
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Tester localement

```bash
python tests/test_local.py
```

Écris des messages comme si tu étais un client cherchant un thérapeute. Sofia répondra!

### 5. Lancer le serveur

```bash
uvicorn agent.main:app --reload --port 8000
```

L'agent sera disponible sur `http://localhost:8000`

---

## 📱 Architecture

```
WhatsApp Client
    ↓
Meta Cloud API / Twilio
    ↓
FastAPI Server (agent/main.py)
    ↓
Claude AI (agent/brain.py)
    ↓
Holisource Tools (agent/holisource_tools.py)
    ↓
Supabase (therapeutes, rendez-vous, chat_logs)
    ↓
Resend (emails) / Twilio (SMS)
```

---

## 📋 Fichiers clés

| Fichier | Purpose |
|---------|---------|
| `agent/main.py` | FastAPI server + webhook handlers |
| `agent/brain.py` | Claude API integration + intent routing |
| `agent/holisource_tools.py` | Business logic (search, book, qualify) |
| `agent/supabase_client.py` | Database client |
| `agent/memory.py` | Conversation history |
| `agent/providers/` | Meta + Twilio adapters |
| `config/` | Configuration files (YAML) |
| `tests/test_local.py` | Terminal chat simulator |

---

## 🔧 Configuration Holisource

### Variables d'environnement

```env
# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Supabase
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGc...

# WhatsApp Provider
WHATSAPP_PROVIDER=meta  # ou twilio

# Si Meta:
META_ACCESS_TOKEN=...
META_PHONE_NUMBER_ID=...
META_VERIFY_TOKEN=holisource-verify

# Si Twilio:
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=...

# Resend (emails)
RESEND_API_KEY=...

# Mistral (modération)
MISTRAL_API_KEY=...

# Server
PORT=8000
ENVIRONMENT=development
```

---

## 🌐 Déployer sur Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "feat: Holisource WhatsApp Agent"
git remote add origin https://github.com/YOUR-USERNAME/holisource-whatsapp-agent.git
git push -u origin main
```

### 2. Connecter Railway

1. Va sur [railway.app](https://railway.app)
2. Clique "New Project"
3. "Deploy from GitHub repo"
4. Sélectionne ton repo

### 3. Configurer les Variables

Dans Railway → Variables, ajoute:

```env
ANTHROPIC_API_KEY=sk-ant-...
SUPABASE_URL=...
SUPABASE_KEY=...
WHATSAPP_PROVIDER=meta
META_ACCESS_TOKEN=...
[etc.]
ENVIRONMENT=production
```

### 4. Configurer le Webhook

Copie l'URL Railway (ex: `https://holisource-agent.up.railway.app`)

**Si Meta Cloud API:**
1. Va sur [developers.facebook.com](https://developers.facebook.com)
2. App → WhatsApp → Configuration
3. Webhook URL: `https://holisource-agent.up.railway.app/webhook`
4. Verify Token: `holisource-verify-2026`

**Si Twilio:**
1. Va sur [console.twilio.com](https://console.twilio.com)
2. Messaging → WhatsApp
3. When a message comes in: `https://holisource-agent.up.railway.app/webhook`

---

## 🧪 Testing

### Local Chat

```bash
python tests/test_local.py
```

Types de messages à tester:

- "Je cherche un reiki à Strasbourg"
- "Quels sont les tarifs ?"
- "Je veux agendar un rendez-vous"
- "Je suis thérapeute, comment m'inscrire?"

### API Testing

```bash
# Envoyer un message test
curl -X POST http://localhost:8000/api/test-message \
  -H "Content-Type: application/json" \
  -d '{"numero": "test-001", "mensaje": "Bonjour Sofia!"}'

# Récupérer l'historique
curl http://localhost:8000/api/history/test-001

# Health check
curl http://localhost:8000/health
```

---

## 🏗️ Architecture du Code

### Flux principal

1. **Webhook** (`agent/main.py`) — Reçoit le message de WhatsApp
2. **Provider** (`agent/providers/meta.py` ou `twilio.py`) — Normalise le format
3. **Memory** (`agent/memory.py`) — Récupère l'historique de Supabase
4. **Brain** (`agent/brain.py`) — Claude détecte l'intention (SEARCH, BOOK, etc.)
5. **Tools** (`agent/holisource_tools.py`) — Exécute les actions (recherche, agendar, etc.)
6. **Response** — Envoie la réponse par WhatsApp

### Intentions détectées

- `SEARCH` — Client cherche un thérapeute
- `BOOK` — Client veut agendar un RDV
- `QUESTION` — Question générale
- `REGISTER` — Veut s'inscrire comme thérapeute
- `ESCALATE` — Veut parler à un humain
- `QUALIFY` — Lead à analyser

---

## 🐛 Troubleshooting

### Supabase connection failed

```
Error: SUPABASE_URL et SUPABASE_KEY manquent dans .env
```

**Solution**: Copie les bonnes valeurs dans `.env`

```bash
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGc...
```

### Claude API error

```
Error: Anthropic API key invalid
```

**Solution**: Vérifie que `ANTHROPIC_API_KEY` commence par `sk-ant-`

### Meta webhook validation fails

```
Error: hub.verify_token invalid
```

**Solution**: Assure-toi que `META_VERIFY_TOKEN` dans `.env` correspond à celui configuré dans Facebook Developers

---

## 📚 Documentation Supabase

Tables principales utilisées:

- **therapeutes** — Profils des thérapeutes
- **rendez_vous** — Réservations des clients
- **disponibilites** — Créneaux libres
- **chat_logs** — Historique des conversations
- **notifications** — Notificies in-app
- **prospects** — Leads qualifiés

---

## 🎨 Charte Holisource

L'agent respecte la tonalité Holisource:
- 💜 Violet comme couleur d'accent
- Français toujours
- Empathique et professionnel
- Pas de spam, propositions naturelles

---

## 📞 Support

Pour les questions ou problèmes:
- 📧 contact@holisource.com
- 🐙 Issues sur GitHub

---

**Version**: 1.0  
**Créé**: 2026-05-08  
**Adapté de**: [AgentKit](https://github.com/Hainrixz/whatsapp-agentkit)
