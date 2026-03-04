import schedule
import time
import subprocess
import os
import logging

# Configuration des logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='/home/ubuntu/voltaire_test/projet_voltaire_farmer/logs/scheduler.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def run_voltaire_session():
    """Lance le script principal pour une session de 20 minutes."""
    logger.info("Démarrage d'une session hebdomadaire automatique...")
    try:
        # On se place dans le bon répertoire pour exécuter le script
        script_path = "/home/ubuntu/voltaire_test/projet_voltaire_farmer/main.py"
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Session terminée avec succès.")
        else:
            logger.error(f"Erreur lors de la session : {result.stderr}")
            
    except Exception as e:
        logger.error(f"Exception lors du lancement de la session : {e}")

# Planification : Mardi et Jeudi à 14h00 (après-midi)
# Ces créneaux correspondent aux recommandations de l'ESIEA
schedule.every().tuesday.at("14:00").do(run_voltaire_session)
schedule.every().thursday.at("14:00").do(run_voltaire_session)

logger.info("Planificateur activé : Sessions prévues les mardis et jeudis à 14h00.")

if __name__ == "__main__":
    # Pour le premier lancement, on peut aussi déclencher une session manuelle si besoin
    # run_voltaire_session() 
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Vérification toutes les minutes
