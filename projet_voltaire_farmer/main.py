import os
import json
import random
import time
import logging
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
CONFIG = {
    "EMAIL": os.getenv("PROJET_VOLTAIRE_EMAIL", "mabiala@et.esiea.fr"),
    "PASSWORD": os.getenv("PROJET_VOLTAIRE_PASSWORD", "Jesusestseigneur2024*"),
    "TARGET_SCORE": 70,
    "SESSION_DURATION_MIN": 20,
    "HEADLESS": True,
    "DEBUG": True
}

# ==========================================
# 📊 LOGGING SETUP
# ==========================================
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/voltaire_farmer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# 🧠 MODULE: AI & HEURISTICS
# ==========================================
class GrammarAI:
    @staticmethod
    def analyze_text(text):
        keywords = ["accord", "conjugaison", "pluriel", "singulier", "genre"]
        found = [k for k in keywords if k in text.lower()]
        return found

    @staticmethod
    def pick_best_answer(question_text, options_elements):
        if not options_elements:
            return None
        scored_options = []
        for option in options_elements:
            try:
                text = option.inner_text().strip()
                if not text: continue
                score = len(text) * 0.1
                keywords = GrammarAI.analyze_text(question_text)
                for k in keywords:
                    if k in text.lower(): score += 5
                if len(text) < 2: score -= 10
                scored_options.append((score, option))
            except: continue
        scored_options.sort(key=lambda x: x[0], reverse=True)
        return scored_options[0][1] if scored_options else None

# ==========================================
# 🕵️ MODULE: STEALTH DRIVER
# ==========================================
class StealthDriver:
    def __init__(self, p):
        self.p = p
        self.browser = None
        self.context = None
        
    def start(self):
        logger.info("Démarrage moteur Stealth...")
        self.browser = self.p.chromium.launch(headless=CONFIG["HEADLESS"])
        self.context = self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="fr-FR"
        )
        page = self.context.new_page()
        page.set_default_timeout(30000)
        return page

    def stop(self):
        if self.browser: self.browser.close()
        logger.info("Moteur arrêté.")

# ==========================================
# 🔐 MODULE: LOGIN MANAGER
# ==========================================
class LoginManager:
    def __init__(self, page):
        self.page = page

    def login(self):
        logger.info(f"Tentative de connexion: {CONFIG['EMAIL']}")
        try:
            self.page.goto("https://compte.groupe-voltaire.fr/login", wait_until="networkidle")
            self.page.fill("input[placeholder='Identifiant']", CONFIG["EMAIL"])
            self.page.fill("input[placeholder='Mot de passe']", CONFIG["PASSWORD"])
            self.page.click("button:has-text('JE ME CONNECTE')")
            self.page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Gestion de la sélection d'univers (ESIEA 2025-2026)
            if "universes" in self.page.url:
                logger.info("Sélection de l'univers 2025-2026...")
                universes = self.page.query_selector_all(".universe-name, h3, h4")
                for u in universes:
                    if "2025-2026" in u.inner_text():
                        u.click()
                        self.page.wait_for_load_state("networkidle")
                        time.sleep(3)
                        break
            
            if "login" not in self.page.url:
                logger.info("Connexion réussie !")
                return True
            return False
        except Exception as e:
            logger.error(f"Erreur connexion: {e}")
            return False

# ==========================================
# 🧭 MODULE: VOLTAIRE FARMER
# ==========================================
class VoltaireFarmer:
    def __init__(self, page):
        self.page = page
        self.ai = GrammarAI()
        
    def navigate_to_module(self, module_name):
        logger.info(f"Recherche du module : {module_name}")
        try:
            # Recherche flexible du module
            module_el = self.page.wait_for_selector(f"text={module_name}", timeout=10000)
            if module_el:
                module_el.click()
                self.page.wait_for_load_state("networkidle")
                # Clic sur le bouton de démarrage
                start_btn = self.page.wait_for_selector("text=Lancer l'entraînement, text=Continuer, text=Commencer", timeout=5000)
                if start_btn:
                    start_btn.click()
                    return True
        except: pass
        return False

    def run_session(self):
        logger.info(f"Session de {CONFIG['SESSION_DURATION_MIN']} min en cours...")
        start_time = time.time()
        while (time.time() - start_time) < (CONFIG["SESSION_DURATION_MIN"] * 60):
            try:
                self.do_exercise()
            except: time.sleep(2)

    def do_exercise(self):
        try:
            question = self.page.wait_for_selector(".question, .enonce", timeout=5000)
            options = self.page.query_selector_all("button.choice, .option, [role='button']")
            best = self.ai.pick_best_answer(question.inner_text(), options)
            if best:
                time.sleep(random.uniform(1, 3))
                best.click()
                time.sleep(1)
                validate = self.page.query_selector("text=Valider, text=OK")
                if validate: validate.click()
                time.sleep(2)
        except: pass

def run_bot():
    with sync_playwright() as p:
        stealth = StealthDriver(p)
        page = stealth.start()
        if LoginManager(page).login():
            farmer = VoltaireFarmer(page)
            for m in ["Orthographe", "Expression", "Courriels"]:
                if farmer.navigate_to_module(m):
                    farmer.run_session()
        stealth.stop()

if __name__ == "__main__":
    run_bot()
