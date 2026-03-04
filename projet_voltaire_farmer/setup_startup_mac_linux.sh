#!/bin/bash

# Chemin absolu du script
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/scheduler.py"
PYTHON_PATH=$(which python3)

# Vérifier si le cron job existe déjà
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH") && echo "Le lancement automatique est déjà configuré." && exit 0

# Ajouter le cron job au démarrage (@reboot)
(crontab -l 2>/dev/null; echo "@reboot nohup $PYTHON_PATH $SCRIPT_PATH > /dev/null 2>&1 &") | crontab -

echo "[SUCCÈS] Le planificateur Projet Voltaire a été ajouté à votre crontab."
echo "Il se lancera désormais automatiquement en arrière-plan à chaque redémarrage."
