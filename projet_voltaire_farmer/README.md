# projet_voltaire_farmer

## Avertissement important

Ce dépôt contient un script d’automatisation basé sur Playwright. **Je ne peux pas aider à l’utiliser pour automatiser/contourner les règles d’une plateforme tierce** (ex. faire des exercices à ta place, “farming”, contournement anti-bot, etc.).  
En revanche, tu peux utiliser ce projet comme **squelette d’automatisation Playwright** pour des cas **autorisés** (tests de ton propre site, QA interne, démos sur sites de test, etc.).

## Prérequis

- Windows 10/11
- Python installé (idéalement via `python.org`)
- Accès Internet (pour télécharger les navigateurs Playwright)

## Installation (Windows / PowerShell)

Depuis le dossier du projet :

```powershell
cd "C:\Users\mabia\OneDrive\Desktop\agent ia"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install playwright schedule
python -m playwright install chromium
```

## Vérifier que Playwright fonctionne (recommandé)

Si tu veux juste vérifier l’installation Playwright, le plus simple est de lancer un script minimal (à créer si besoin) qui ouvre une page publique de test (ex. `https://example.com`) et prend une capture.  
Si tu veux, je peux ajouter ce script “demo” au projet.

## Fichiers et dossiers

- `main.py` : script principal (Playwright)
- `data/` : fichiers de données (ex. `ua_pool.json`, etc.)
- `logs/` : logs (créé automatiquement si tu l’ajoutes / si le script le fait)
- `screenshots/` : captures d’écran de debug

## Configuration (sécurité)

Ne mets **jamais** un mot de passe en dur dans le code.

Le script lit les identifiants via des variables d’environnement (voir `CONFIG` dans `main.py`).  
Exemple (PowerShell) :

```powershell
$env:PROJET_VOLTAIRE_EMAIL="ton_email"
$env:PROJET_VOLTAIRE_PASSWORD="ton_mot_de_passe"
```

> Conseil : si tu as déjà partagé un mot de passe dans un chat/terminal, **change-le**.

## Lancer

Dans un terminal PowerShell avec le venv activé :

```powershell
cd "C:\Users\mabia\OneDrive\Desktop\agent ia\projet_voltaire_farmer"
python main.py
```

## Dépannage rapide

- Si le script “quitte immédiatement” :
  - Vérifie que le venv est activé.
  - Lance `python -c "import playwright; print('ok')"` pour confirmer l’import.
  - Lance `python -m playwright install chromium`.
- Si tu n’as aucun log :
  - Crée `logs/` et relance, ou adapte `main.py` pour créer `logs/` avant le `FileHandler`.

