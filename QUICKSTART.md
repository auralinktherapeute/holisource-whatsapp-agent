# ⚡ Quick Start — 5 minutes

Pour tester l'agent Sofia localement **maintenant**.

---

## 🚀 3 commandes pour démarrer

```bash
# 1️⃣ Copier la configuration
cp .env.example .env

# 2️⃣ Installer les dépendances
pip install -r requirements.txt

# 3️⃣ Lancer le test local
python tests/test_local.py
```

---

## 🔑 Ajouter tes clés API

Édite `.env` et ajoute **AU MINIMUM**:

```env
MISTRAL_API_KEY=YOUR_KEY_HERE
SUPABASE_URL=https://dqmujlqxpmcwscztrrdt.supabase.co
SUPABASE_KEY=YOUR_KEY_HERE
WHATSAPP_PROVIDER=meta  # ou twilio
```

Où obtenir les clés:
- **Mistral**: https://console.mistral.ai/
- **Supabase**: Déjà configuré pour Holisource
- **Meta**: https://developers.facebook.com/ (si tu veux tester le vrai webhook plus tard)

---

## 💬 Converser avec Sofia

Une fois `python tests/test_local.py` lancé:

```
Tú: Je cherche un thérapeute holistique à Strasbourg
🤖 Sofia: ✨ Voici ce que j'ai trouvé...

Tú: Quels sont les tarifs?
🤖 Sofia: Les tarifs varient selon le thérapeute...

Tú: Je veux agendar un rendez-vous
🤖 Sofia: Bien sûr! Pour agendar...

Tú: salir
✅ Test finalizado.
```

---

## 🌐 Lancer le serveur (optionnel)

```bash
# Terminal 1
uvicorn agent.main:app --reload --port 8000

# Terminal 2 (tester)
curl http://localhost:8000/health
# Résultat: {"status": "ok", ...}
```

---

## 📚 Où aller après?

1. **Comprendre le projet**: Lis `README.md`
2. **Configuration complète**: Lis `SETUP.md`
3. **Structure du code**: Lis `INDEX.md`
4. **Déployer en production**: Lis `SETUP.md` → Phase 7

---

**C'est tout!** 🎉 Sofia fonctionne maintenant localement.

Pour plus de détails, consulte `SETUP.md`.
