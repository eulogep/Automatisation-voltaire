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
        
        # Sélection de l'univers 2025-2026
        logger.info("Recherche de l'univers 2025-2026...")
        # On clique sur le texte directement car les sélecteurs de boutons sont capricieux
        universes = self.page.query_selector_all("div")
        for u in universes:
            try:
                text = u.inner_text()
                if "2025-2026" in text and "ACCÉDER" in text:
                    u.click()
                    logger.info("Univers sélectionné.")
                    time.sleep(5)
                    return True
            except: continue
        return "universes" not in self.page.url

    def start_module(self, module_name):
        logger.info(f"Démarrage du module {module_name}...")
        try:
            self.page.click(f"text={module_name}")
            time.sleep(3)
            btn = self.page.wait_for_selector("text=Lancer l'entraînement, text=Continuer, text=Commencer", timeout=10000)
            if btn:
                btn.click()
                time.sleep(5)
                return True
        except: pass
        return False

    def solve_exercises(self):
        logger.info("Début de la résolution des exercices...")
        end_time = time.time() + (CONFIG["SESSION_DURATION_MIN"] * 60)
        
        while time.time() < end_time:
            try:
                # 1. Attendre l'exercice
                self.page.wait_for_selector(".sentence, .question, .word", timeout=15000)
                
                # 2. Stratégie de résolution : 
                # On simule un clic aléatoire sur un mot ou sur "Pas de faute"
                # Le but est de progresser, l'IA de Voltaire s'adaptera
                words = self.page.query_selector_all("span.word, .point-and-click span")
                
                if words and random.random() > 0.2:
                    target = random.choice(words)
                    logger.info("Clic sur un mot...")
                    target.click()
                else:
                    no_error = self.page.query_selector("text=Il n'y a pas de faute, .no-error-button")
                    if no_error:
                        logger.info("Clic sur 'Il n'y a pas de faute'...")
                        no_error.click()
                
                time.sleep(2)
                # 3. Validation
                validate = self.page.query_selector("text=Valider, text=OK, .btn-validate")
                if validate: validate.click()
                
                time.sleep(3) # Feedback
                # 4. Suite
                next_btn = self.page.query_selector("text=Suivant, text=Continuer")
                if next_btn: next_btn.click()
                
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
                    # Revenir au menu après chaque module
                    page.goto("https://compte.groupe-voltaire.fr/user/universes")
                    time.sleep(5)
                    # Re-cliquer sur l'univers pour revenir aux modules
                    bot.login() 
        
        browser.close()

if __name__ == "__main__":
    run()
