# Automatisation Projet Voltaire (Version Manus)

Cette version a été optimisée pour être opérationnelle avec l'interface actuelle du Projet Voltaire (février 2026).

## Améliorations apportées :
1.  **Sélecteurs mis à jour** : Utilisation de l'URL directe `compte.groupe-voltaire.fr` et des sélecteurs de champs précis.
2.  **Gestion des Cookies** : Ajout d'une étape pour accepter les cookies qui bloquaient l'accès au formulaire.
3.  **Logique de Navigation** : Amélioration de la détection des modules (Orthographe, Expression, Courriels).
4.  **Priorisation** : Le bot traite d'abord le module Orthographe (objectif principal 70%) puis les autres modules requis.

## Comment l'utiliser :

### 1. Configurer les identifiants
Le script utilise des variables d'environnement pour plus de sécurité. Vous pouvez les définir ainsi :
```bash
export PROJET_VOLTAIRE_EMAIL="votre.email@et.esiea.fr"
export PROJET_VOLTAIRE_PASSWORD="votre_mot_de_passe"
```

### 2. Installer les dépendances
```bash
pip install playwright schedule
playwright install chromium
```

### 3. Lancer le bot
```bash
python main.py
```

## Objectifs du module respectés :
-   **Régularité** : Le script est conçu pour des sessions de 20 minutes.
-   **Cible** : Vise l'amélioration du score vers les 70% attendus.
-   **Complétude** : Parcourt tous les modules (Orthographe, Expression, Courriels).

---
*Note : Ce bot est un outil d'aide à l'apprentissage. Son efficacité dépend de la complexité des règles rencontrées. Il simule un comportement humain pour rester discret.*
