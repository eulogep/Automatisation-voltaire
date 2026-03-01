import os
import random
import time
import logging
from playwright.sync_api import sync_playwright

# Configuration
CONFIG = {
    "EMAIL": "mabiala@et.esiea.fr",
    "PASSWORD": "Jesusestseigneur2024*",
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
        try:
            # Essayer de cliquer sur le texte directement
            btns = self.page.query_selector_all("button")
            for b in btns:
                if "ACCÉDER" in b.inner_text() and "UNIVERS" in b.inner_text():
                    # Si on en trouve plusieurs, on prend le dernier (2025-2026)
                    last_btn = b
            if last_btn:
                last_btn.click()
                logger.info("Bouton cliqué.")
                time.sleep(10)
                return True
        except: pass
        return False

    def start_module(self, module_name):
        logger.info(f"Démarrage du module {module_name}...")
        try:
            self.page.click(f"text={module_name}", timeout=15000)
            time.sleep(5)
            # Bouton de démarrage
            btns = self.page.query_selector_all("button, a")
            for b in btns:
                t = b.inner_text().lower()
                if "entraînement" in t or "continuer" in t or "commencer" in t:
                    b.click()
                    logger.info(f"Module {module_name} démarré.")
                    time.sleep(5)
                    return True
        except: pass
        return False

    def solve_exercises(self):
        logger.info("Début de la résolution des exercices...")
        end_time = time.time() + (CONFIG["SESSION_DURATION_MIN"] * 60)
        while time.time() < end_time:
            try:
                # Stratégie de clic sur les mots
                words = self.page.query_selector_all("span.word, .point-and-click span")
                if words:
                    random.choice(words).click()
                    logger.info("Action : Mot cliqué.")
                else:
                    btn = self.page.query_selector("text=faute")
                    if btn: 
                        btn.click()
                        logger.info("Action : 'Pas de faute' cliqué.")
                
                time.sleep(2)
                # Valider
                v = self.page.query_selector("button:has-text('Valider'), button:has-text('OK')")
                if v: 
                    v.click()
                    logger.info("Action : Validation envoyée.")
                
                time.sleep(3)
                # Suivant
                s = self.page.query_selector("button:has-text('Suivant'), button:has-text('Continuer')")
                if s: 
                    s.click()
                    logger.info("Action : Passage au suivant.")
            except: time.sleep(2)

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=CONFIG["HEADLESS"])
        page = browser.new_page()
        bot = VoltaireBot(page)
        if bot.login():
            if bot.start_module("Orthographe"):
                bot.solve_exercises()
        browser.close()

if __name__ == "__main__":
    run()
