# 🚀 Checkpoint Déploiement — Holisource WhatsApp Agent

**Date** : 2026-05-09  
**État** : En cours de déploiement Railway  
**Qui continue** : Claude Cowork

---

## ✅ COMPLÉTÉ

### 1. Intégration Mistral API
- ✅ Remplacé Anthropic Claude par Mistral (`mistralai` SDK)
- ✅ Fichier `agent/brain.py` : `from mistralai.client.sdk import Mistral`
- ✅ Changé model → `mistral-large-latest`
- ✅ Mistral API Key configurée dans `.env` : `b9lSDfVSDj659SB4lBvL6LMkNOwXSfLw`

### 2. Configuration locale
- ✅ `.env` rempli avec toutes les variables
- ✅ Supabase configuré (URL + Anon Key)
- ✅ Logging désactivé temporairement (schéma chat_logs incompatible)
- ✅ Sofia répond correctement via Mistral

### 3. Git & GitHub
- ✅ Repository GitHub créé : `https://github.com/auralinktherapeute/holisource-whatsapp-agent`
- ✅ Code pushé avec commit : "feat: Mistral API integration + Holisource WhatsApp Agent ready for Railway deployment"
- ✅ Tous les fichiers sur main branch

### 4. Railroad (partiellement)
- ✅ Compte Railway créé (plan TRIAL, $5 crédit gratuit pendant 30 jours)
- ✅ 2 projets existants (mellow-motivation, profound-gratitude)
- ⏳ Besoin de supprimer 1 projet OU créer le nouveau

---

## 🔄 À FAIRE MAINTENANT (pour Claude Cowork)

### ÉTAPE 1 — Supprimer un projet existant (optionnel mais recommandé)

**Ou** créer directement le nouveau sans supprimer (si crédits suffisent).

Si suppression nécessaire :
```
1. Clique sur "mellow-motivation"
2. Settings (⚙️) → Danger Zone → Delete Project
3. Confirme en tapant le nom
4. Supprimé ✓
```

### ÉTAPE 2 — Créer nouveau projet Railway

```
1. Railway.app → "+ New" (bouton violet)
2. "Project"
3. "Deploy from GitHub Repo"
4. Cherche : auralinktherapeute/holisource-whatsapp-agent
5. Clique → déploiement auto-commence
```

Railway va :
- Cloner le repo GitHub
- Builder l'image Docker (voir Dockerfile à la racine)
- Lancer le serveur FastAPI
- T'assigner une URL publique (ex: `https://holisource-agent-xyz.up.railway.app`)

### ÉTAPE 3 — Ajouter variables d'environnement

Une fois que le service "app" apparaît dans Railway :

```
Clique "Variables" → ajoute ces clés-valeurs :

MISTRAL_API_KEY=b9lSDfVSDj659SB4lBvL6LMkNOwXSfLw
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRxbXVqbHF4cG1jd3NjenRycmR0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk0MjM5NzgsImV4cCI6MjA4NDk5OTk3OH0.8RbSZphL-Ee78Ruo1_QE4WJ0tU4tkUl9w6Mk6uq7NKg
WHATSAPP_PROVIDER=meta
META_ACCESS_TOKEN=test_placeholder
META_PHONE_NUMBER_ID=test_placeholder
META_VERIFY_TOKEN=holisource-verify
RESEND_API_KEY=test
PORT=8000
ENVIRONMENT=production
```

Railway redéploiera automatiquement après chaque variable.

### ÉTAPE 4 — Vérifier le déploiement

Attends que tu vois :
- ✅ "Deployment Successful" (ou "Running")
- URL publique affichée (ex: `https://holisource-agent-...up.railway.app`)
- Logs verts (pas d'erreurs)

Test de la route health :
```bash
curl https://holisource-agent-....up.railway.app/health
# Doit retourner : {"status":"ok","service":"holisource-whatsapp-agent"}
```

### ÉTAPE 5 — Configurer WhatsApp (après)

Une fois l'URL Railway confirmée, configurer :

**Si Meta Cloud API** :
1. Va sur https://developers.facebook.com
2. Ton app → WhatsApp → Configuration
3. Webhook URL : `https://holisource-agent-....up.railway.app/webhook`
4. Verify Token : `holisource-verify`
5. Souscrire aux événements "messages"

**Si Twilio** :
1. Va sur https://console.twilio.com
2. Messaging → WhatsApp Sandbox
3. "When a message comes in" : `https://holisource-agent-....up.railway.app/webhook`

---

## 📋 Fichiers clés

| Fichier | Rôle | État |
|---------|------|------|
| `agent/brain.py` | Moteur Mistral IA | ✅ Fait |
| `agent/supabase_client.py` | Client Supabase | ✅ Fait |
| `agent/holisource_tools.py` | Outils métier | ✅ Fait |
| `agent/main.py` | Serveur FastAPI | ✅ Fait |
| `Dockerfile` | Image Docker | ✅ Fait |
| `requirements.txt` | Dépendances Python | ✅ Fait |
| `.env` | Variables locales | ✅ Rempli |
| `.env.example` | Template | ✅ Fait |

---

## 🔑 Secrets & URLs

| Secret | Valeur | Où |
|--------|--------|-----|
| MISTRAL_API_KEY | `b9lSDfVSDj659SB4lBvL6LMkNOwXSfLw` | Railway Variables |
| SUPABASE_URL | `https://dqmujlqxpmcwscztrrdt.supabase.co` | Railway Variables |
| SUPABASE_KEY | (voir ci-dessus) | Railway Variables |
| GitHub Repo | `https://github.com/auralinktherapeute/holisource-whatsapp-agent` | ✅ Pushé |
| WhatsApp Webhook URL | `https://holisource-agent-....up.railway.app/webhook` | À configurer après |

---

## ⚠️ Notes importantes

1. **Chat logs temporairement désactivés** — Supabase RLS a des problèmes de schéma. À corriger après :
   - Normaliser la table `chat_logs` dans Supabase
   - Réactiver RLS
   - Réactiver logging dans `agent/supabase_client.py`

2. **Plan Railway TRIAL** — $5 crédit gratuit pendant 30 jours. Suffisant pour tester.

3. **Docker** — Railway utilise le `Dockerfile` à la racine. Bien configuré pour FastAPI.

4. **Health endpoint** — `/health` retourne `{"status":"ok","service":"holisource-whatsapp-agent"}` si tout marche.

---

## 🎯 Checklist pour Claude Cowork

- [ ] Créer projet Railway "holisource-whatsapp-agent"
- [ ] Variables d'environnement ajoutées
- [ ] Déploiement réussi (URL publique)
- [ ] Test `/health` endpoint
- [ ] Configurer webhook WhatsApp (Meta ou Twilio)
- [ ] Tester Sofia depuis WhatsApp

---

**Prochaines grandes étapes** (après déploiement) :

1. **Intégration WhatsApp** — Connecter l'agent au vrai numéro WhatsApp
2. **Logging Supabase** — Fixer le schéma chat_logs
3. **Optimisations** — Performance, gestion erreurs, monitoring
4. **Production** — Vrai déploiement, upgrade plan Railway si needed

---

**Version** : 1.0  
**Créé par** : Gérald Henry  
**Continué par** : Claude Cowork  
**Statut** : Deployment in progress 🚀
