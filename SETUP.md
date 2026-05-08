# 🚀 Guide de Mise en Place — Holisource WhatsApp Agent

Ce guide te montre étape par étape comment configurer et déployer l'agent Sofia.

---

## ✅ Pré-requis

- Python 3.11+ (`python3 --version`)
- Git (`git --version`)
- Compte Supabase (dqmujlqxpmcwscztrrdt)
- API Key Anthropic (Claude)
- Compte WhatsApp (Meta Cloud API OU Twilio)
- (Optionnel) Railway pour production

---

## 📝 Phase 1 — Configuration locale

### 1.1 — Cloner le repository

```bash
cd /Users/geraldhenry/claude
git clone https://github.com/TODO/holisource-whatsapp-agent.git
cd holisource-whatsapp-agent
```

### 1.2 — Créer le fichier `.env`

```bash
cp .env.example .env
```

### 1.3 — Remplir les variables d'environnement

Édite `.env` et ajoute tes clés. Voici comment les obtenir:

#### Mistral API Key

1. Va sur https://console.mistral.ai/
2. Crée un compte ou connecte-toi
3. API Keys → Créer une clé
4. Copie la clé
5. Colle dans `.env`:

```env
MISTRAL_API_KEY=...
```

#### Supabase

Supabase est déjà configuré pour Holisource:

```env
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

(La clé anon est déjà publique — c'est ok, RLS Supabase protège les données)

#### WhatsApp Provider — Choix

**Option 1: Meta Cloud API (recommandé pour production)**

1. Va sur https://developers.facebook.com/
2. Crée une app type "Business"
3. Ajoute le produit "WhatsApp"
4. WhatsApp → API Setup
5. Copie:
   - Access Token (permanente) → `META_ACCESS_TOKEN`
   - Phone Number ID → `META_PHONE_NUMBER_ID`
   - Crée un Verify Token → `META_VERIFY_TOKEN=holisource-verify`

```env
WHATSAPP_PROVIDER=meta
META_ACCESS_TOKEN=EAAx...
META_PHONE_NUMBER_ID=102...
META_VERIFY_TOKEN=holisource-verify
```

**Option 2: Twilio (facile pour tester)**

1. Va sur https://www.twilio.com/
2. Crée un compte et valide ton téléphone
3. Console → Account Info
4. Copie:
   - Account SID → `TWILIO_ACCOUNT_SID`
   - Auth Token → `TWILIO_AUTH_TOKEN`
5. Messaging → Try it Out → WhatsApp
6. Active le sandbox → Copie le numéro asigné

```env
WHATSAPP_PROVIDER=twilio
TWILIO_ACCOUNT_SID=ACx...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=whatsapp:+...
```

#### Resend (Emails transactionnels)

1. Va sur https://resend.com/
2. Dashboard → API Keys
3. Copie la clé

```env
RESEND_API_KEY=re_...
```

### 1.4 — Vérifier la configuration

```bash
# Vérifier Python
python3 --version  # Doit être >= 3.11

# Vérifier que .env existe
cat .env | head -5  # Affiche les premières lignes

# Vérifier la structure
ls -la
# Doit afficher: agent/, config/, knowledge/, tests/, requirements.txt, .env, CLAUDE.md, etc.
```

---

## 🛠️ Phase 2 — Installation

### 2.1 — Créer un virtual environment (optionnel mais recommandé)

```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 2.2 — Installer les dépendances

```bash
pip install -r requirements.txt
```

Output attendu:
```
Successfully installed anthropic-0.40.0 fastapi-0.104.0 supabase-2.0.0 ...
```

### 2.3 — Vérifier l'installation

```bash
python3 -c "import anthropic, supabase, fastapi; print('✅ Dépendances OK')"
```

---

## 🧪 Phase 3 — Test local

### 3.1 — Chat local

```bash
python tests/test_local.py
```

Résultat attendu:
```
============================================================
   🧪 Holisource WhatsApp Agent — Test Local
============================================================

Escribe mensajes como si fueras un cliente...

Tú: Hola, busco un reiki en Strasbourg
🤖 Sofia: ✨ Voici ce que j'ai trouvé pour toi...
```

### 3.2 — Tester différents scénarios

```
# Recherche thérapeute
Tú: Je cherche un thérapeute holistique à Strasbourg

# Agendar
Tú: Je veux agendar un rendez-vous

# Question générale
Tú: Qu'est-ce que la méditation ?

# S'inscrire comme thérapeute
Tú: Je suis thérapeute, comment m'inscrire ?

# Quitter
Tú: salir
```

### 3.3 — Si erreur...

**Erreur: ModuleNotFoundError**
```
pip install -r requirements.txt
```

**Erreur: SUPABASE_KEY invalid**
Vérifie que `.env` contient les bonnes valeurs

**Erreur: Mistral API error**
Vérifie que `MISTRAL_API_KEY` est correct dans `.env`

---

## 🚀 Phase 4 — Lancer le serveur local

### 4.1 — Démarrer le serveur

```bash
uvicorn agent.main:app --reload --port 8000
```

Output attendu:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4.2 — Vérifier qu'il fonctionne

```bash
# Dans un autre terminal
curl http://localhost:8000
# Retour: {"status": "ok", "service": "holisource-whatsapp-agent", ...}
```

### 4.3 — Accéder aux endpoints

- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs
- OpenAPI: http://localhost:8000/openapi.json

---

## 📱 Phase 5 — Connecter WhatsApp

### 5.1 — Si tu utilises Meta Cloud API

1. Copie l'URL du webhook que tu fournieras:
   - Local: `http://localhost:8000/webhook` (pour tester en localhost, utilise ngrok)
   - Production: `https://ton-domain.com/webhook`

2. Va sur [developers.facebook.com](https://developers.facebook.com)
3. Ton app → WhatsApp → Configuration
4. Webhook URL: `https://ton-domain.com/webhook`
5. Verify Token: `holisource-verify` (doit correspondre à `META_VERIFY_TOKEN`)
6. Souscrire aux événements "messages"
7. Tester

### 5.2 — Si tu utilises Twilio

1. Copie l'URL du webhook
2. Va sur [console.twilio.com](https://console.twilio.com)
3. Messaging → WhatsApp Sandbox Settings
4. "When a message comes in": `https://ton-domain.com/webhook`
5. Méthode: POST
6. Sauvegarder

### 5.3 — Tester le webhook

Envoie un message à Sofia depuis WhatsApp et vérifie que la réponse arrive.

Logs attendus:
```
📱 Mensaje de +33612345678: Bonjour Sofia!
...
✅ Respuesta enviada a +33612345678
```

---

## 🐳 Phase 6 — Docker (optionnel, pour production)

### 6.1 — Build l'image Docker

```bash
docker compose build
```

### 6.2 — Lancer le conteneur

```bash
docker compose up
```

Output:
```
agent  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6.3 — Arrêter

```bash
docker compose down
```

---

## 🚢 Phase 7 — Déployer sur Railway

### 7.1 — Préparer pour le deploy

```bash
# Actualiser .gitignore (production)
cat > .gitignore << 'EOF'
.env
.env.*.local
*.db
*.sqlite3
__pycache__/
venv/
.vscode/
.idea/
EOF

# Vérifier l'absence de secrets
git status
# Ne doit pas inclure .env
```

### 7.2 — Committer et pusher

```bash
git add .
git commit -m "feat: Holisource WhatsApp Agent ready for production"
git push -u origin main
```

### 7.3 — Créer un repo GitHub (si pas déjà fait)

```bash
# Si tu n'as pas de repo GitHub
git init
git add .
git commit -m "Initial commit: Holisource WhatsApp Agent"
git remote add origin https://github.com/YOUR-USERNAME/holisource-whatsapp-agent.git
git push -u origin main
```

### 7.4 — Connecter Railway

1. Va sur [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub repo"
3. Sélectionne ton repo
4. Railway t'assigne une URL publique (ex: `https://holisource-agent.up.railway.app`)

### 7.5 — Configurer les variables d'environnement

1. Dans Railway → Project → Variables
2. Ajoute toutes les variables de `.env`:

```
MISTRAL_API_KEY=...
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
WHATSAPP_PROVIDER=meta
META_ACCESS_TOKEN=...
[etc.]
ENVIRONMENT=production
```

### 7.6 — Configurer le webhook WhatsApp

Meta Cloud API:
- Webhook URL: `https://holisource-agent.up.railway.app/webhook`
- Verify Token: `holisource-verify`

Twilio:
- When a message comes in: `https://holisource-agent.up.railway.app/webhook`

### 7.7 — Tester en production

Envoie un message WhatsApp à ton numéro assigné. Sofia doit répondre!

Vérifie les logs Railway:
```
Railway → Project → Logs
```

Cherche:
```
✅ Respuesta enviada a ...
```

---

## 🎯 Checklist finale

- [ ] Python 3.11+ installé
- [ ] `.env` rempli avec toutes les clés
- [ ] `pip install -r requirements.txt` ✅
- [ ] `python tests/test_local.py` fonctionne
- [ ] `uvicorn agent.main:app` fonctionne
- [ ] Supabase health check OK
- [ ] WhatsApp provider configuré (Meta OU Twilio)
- [ ] Webhook WhatsApp configuré et testé
- [ ] Message test reçu et répondu ✅
- [ ] (Optionnel) Déployé sur Railway

---

## 📞 Support & Troubleshooting

### Common issues

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| `SUPABASE_KEY invalid` | Vérifie `.env` (clé anon de Supabase) |
| `Anthropic API error` | Vérifie `ANTHROPIC_API_KEY` (commence par `sk-ant-`) |
| `Meta webhook fails` | Vérifie `META_VERIFY_TOKEN` dans `.env` et Meta Developers |
| `No messages received` | Vérifie que le webhook URL est correct et accessible |

### Debug mode

Activa logs détaillés:

```bash
# Terminal
ENVIRONMENT=development python tests/test_local.py

# Ou dans .env
ENVIRONMENT=development
```

---

## 🎉 Prochaines étapes

Une fois que l'agent est en production:

1. **Monitorer** — Vérifie les logs Railway régulièrement
2. **Optimiser le prompt** — Ajuste `config/prompts_holisource.yaml` selon les retours
3. **Intégrer Calendly** — Connecte les calendriers des thérapeutes
4. **Analyser les conversations** — Exporte les chats_logs pour améliorer Sofia
5. **Escalade commerciale** — Mets en place les leads qualifiés → équipe de vente

---

**Créé**: 2026-05-08  
**Version**: 1.0  
**Pour**: Holisource.com
