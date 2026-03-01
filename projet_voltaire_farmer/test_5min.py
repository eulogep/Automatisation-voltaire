import os
import json
import random
import time
import logging
from playwright.sync_api import sync_playwright

# Configuration pour le test de 5 minutes
CONFIG = {
    "EMAIL": "mabiala@et.esiea.fr",
    "PASSWORD": "Jesusestseigneur2024*",
    "SESSION_DURATION_MIN": 5,
    "HEADLESS": True
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VoltaireBot:
    def __init__(self, page):
        self.page = page

    def login(self):
        logger.info(f"Connexion pour {CONFIG['EMAIL']}...")
        self.page.goto("https://compte.groupe-voltaire.fr/login")
        self.page.fill("input[placeholder='Identifiant']", CONFIG["EMAIL"])
        self.page.fill("input[placeholder='Mot de passe']", CONFIG["PASSWORD"])
        self.page.click("button:has-text('JE ME CONNECTE')")
        self.page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        logger.info("Recherche de l'univers 2025-2026...")
        # Sélection de l'univers par clic sur le texte
        try:
            universes = self.page.query_selector_all("div")
            for u in universes:
                text = u.inner_text()
                if "2025-2026" in text and "ACCÉDER" in text:
                    u.click()
                    logger.info("Univers 2025-2026 sélectionné.")
                    time.sleep(5)
                    return True
        except Exception as e:
            logger.error(f"Erreur sélection univers : {e}")
        return False

    def start_module(self, module_name):
        logger.info(f"Démarrage du module {module_name}...")
        try:
            self.page.click(f"text={module_name}")
            time.sleep(3)
            btn = self.page.wait_for_selector("text=Lancer l'entraînement, text=Continuer, text=Commencer", timeout=10000)
            if btn:
                btn.click()
                logger.info(f"Module {module_name} lancé avec succès.")
                time.sleep(5)
                return True
        except Exception as e:
            logger.warning(f"Impossible de lancer le module {module_name} : {e}")
        return False

    def solve_exercises(self):
        logger.info("Début de la résolution des exercices (5 min)...")
        end_time = time.time() + (CONFIG["SESSION_DURATION_MIN"] * 60)
        
        while time.time() < end_time:
            try:
                # Attendre l'exercice
                self.page.wait_for_selector(".sentence, .question, .word", timeout=15000)
                
                # Stratégie de clic
                words = self.page.query_selector_all("span.word, .point-and-click span")
                if words and random.random() > 0.2:
                    target = random.choice(words)
                    logger.info(f"Action : Clic sur un mot ({target.inner_text().strip()})")
                    target.click()
                else:
                    no_error = self.page.query_selector("text=Il n'y a pas de faute, .no-error-button")
                    if no_error:
                        logger.info("Action : Clic sur 'Il n'y a pas de faute'")
                        no_error.click()
                
                time.sleep(2)
                # Validation
                validate = self.page.query_selector("text=Valider, text=OK, .btn-validate")
                if validate: 
                    validate.click()
                    logger.info("Validation envoyée.")
                
                time.sleep(3) # Attente feedback
                
                # Suite
                next_btn = self.page.query_selector("text=Suivant, text=Continuer")
                if next_btn: 
                    next_btn.click()
                    logger.info("Passage à l'exercice suivant.")
                
            except Exception as e:
                logger.debug(f"Attente exercice... {e}")
                time.sleep(2)

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CONFIG["HEADLESS"])
        page = browser.new_page()
        bot = VoltaireBot(page)
        
        if bot.login():
            if bot.start_module("Orthographe"):
                bot.solve_exercises()
        
        browser.close()
        logger.info("Session de test de 5 minutes terminée.")

if __name__ == "__main__":
    run_test()
