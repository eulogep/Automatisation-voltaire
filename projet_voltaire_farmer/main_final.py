import os
import json
import random
import time
import logging
from playwright.sync_api import sync_playwright

# Configuration
CONFIG = {
    "EMAIL": os.getenv("PROJET_VOLTAIRE_EMAIL", "mabiala@et.esiea.fr"),
    "PASSWORD": os.getenv("PROJET_VOLTAIRE_PASSWORD", "Jesusestseigneur2024*"),
    "SESSION_DURATION_MIN": 20,
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
        
        logger.info("Sélection de l'univers 2025-2026...")
        # Utilisation de get_by_role pour éviter les erreurs de sélecteur CSS
        btns = self.page.get_by_role("button", name="ACCÉDER À L'UNIVERS")
        count = btns.count()
        if count >= 2:
            btns.nth(1).click()
            logger.info("Bouton d'accès à l'univers 2025-2026 cliqué.")
            time.sleep(10)
            return True
        elif count == 1:
            btns.nth(0).click()
            logger.info("Seul bouton d'accès à l'univers cliqué.")
            time.sleep(10)
            return True
        return False

    def start_module(self, module_name):
        logger.info(f"Démarrage du module {module_name}...")
        try:
            # Recherche par texte exacte ou partielle
            module_el = self.page.get_by_text(module_name, exact=False).first
            if module_el:
                module_el.click()
                time.sleep(5)
                # Clic sur le bouton de démarrage
                start_btn = self.page.get_by_role("button", name="entraînement").or_(self.page.get_by_text("Continuer")).or_(self.page.get_by_text("Commencer")).first
                if start_btn:
                    start_btn.click()
                    logger.info(f"Module {module_name} démarré.")
                    time.sleep(5)
                    return True
        except Exception as e:
            logger.warning(f"Impossible de démarrer {module_name} : {e}")
        return False

    def solve_exercises(self):
        logger.info("Début de la résolution des exercices...")
        end_time = time.time() + (CONFIG["SESSION_DURATION_MIN"] * 60)
        
        while time.time() < end_time:
            try:
                # Attendre l'exercice (détection par les mots cliquables)
                self.page.wait_for_selector("span.word, .point-and-click span", timeout=15000)
                
                words = self.page.query_selector_all("span.word, .point-and-click span")
                if words and random.random() > 0.2:
                    target = random.choice(words)
                    logger.info("Action : Clic sur un mot")
                    target.click()
                else:
                    no_error = self.page.get_by_text("Il n'y a pas de faute").first
                    if no_error:
                        logger.info("Action : Clic sur 'Il n'y a pas de faute'")
                        no_error.click()
                
                time.sleep(2)
                # Validation
                validate = self.page.get_by_role("button", name="Valider").or_(self.page.get_by_text("OK")).first
                if validate: 
                    validate.click()
                    logger.info("Validation envoyée.")
                
                time.sleep(3)
                # Suite
                next_btn = self.page.get_by_text("Suivant").or_(self.page.get_by_text("Continuer")).first
                if next_btn: 
                    next_btn.click()
                    logger.info("Passage à l'exercice suivant.")
                
            except Exception as e:
                logger.debug(f"Attente exercice... {e}")
                time.sleep(2)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CONFIG["HEADLESS"])
        page = browser.new_page()
        bot = VoltaireBot(page)
        
        if bot.login():
            for module in ["Orthographe", "Expression", "Courriels"]:
                if bot.start_module(module):
                    bot.solve_exercises()
                    page.goto("https://compte.groupe-voltaire.fr/user/universes")
                    time.sleep(5)
                    bot.login()
        
        browser.close()

if __name__ == "__main__":
    run()
