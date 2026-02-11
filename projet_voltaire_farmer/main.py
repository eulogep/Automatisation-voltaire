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
    "EMAIL": os.getenv("PROJET_VOLTAIRE_EMAIL", "VOTRE_EMAIL@et.esiea.fr"),
    "PASSWORD": os.getenv("PROJET_VOLTAIRE_PASSWORD", "VOTRE_MOT_DE_PASSE"),
    "TARGET_SCORE": 70,
    "SESSION_DURATION_MIN": 20,
    "HEADLESS": True,  # Mode invisible par défaut pour Manus
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
    """Simule une IA pour choisir les réponses"""
    
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
                score = 0
                score += len(text) * 0.1
                keywords = GrammarAI.analyze_text(question_text)
                for k in keywords:
                    if k in text.lower():
                        score += 5
                if len(text) < 2:
                    score -= 10
                scored_options.append((score, option))
            except:
                continue
            
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
        self.page = None
        
    def start(self):
        logger.info("Démarrage moteur Stealth (Playwright)...")
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        self.browser = self.p.chromium.launch(
            headless=CONFIG["HEADLESS"],
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        self.context = self.browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={'width': 1280, 'height': 720},
            locale="fr-FR"
        )
        
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)
        return self.page

    def stop(self):
        if self.context: self.context.close()
        if self.browser: self.browser.close()
        logger.info("Moteur arrêté.")

    def human_delay(self, min_s=1.0, max_s=3.0):
        time.sleep(random.uniform(min_s, max_s))

# ==========================================
# 🔐 MODULE: LOGIN MANAGER
# ==========================================
class LoginManager:
    def __init__(self, page):
        self.page = page

    def login(self):
        logger.info(f"Tentative de connexion: {CONFIG['EMAIL']}")
        try:
            # Aller directement à la page de login
            self.page.goto("https://compte.groupe-voltaire.fr/login", wait_until="networkidle")
            
            # Gérer les cookies si présents
            try:
                cookie_btn = self.page.wait_for_selector("text=Accepter et fermer", timeout=5000)
                if cookie_btn: cookie_btn.click()
            except:
                pass

            # Remplissage
            self.page.fill("input[placeholder='Identifiant']", CONFIG["EMAIL"])
            time.sleep(random.uniform(0.5, 1.5))
            self.page.fill("input[placeholder='Mot de passe']", CONFIG["PASSWORD"])
            time.sleep(random.uniform(0.5, 1.5))
            
            # Clic Submit
            self.page.click("button:has-text('JE ME CONNECTE')")
            
            # Vérification
            self.page.wait_for_load_state("networkidle")
            if "login" not in self.page.url:
                logger.info("Connexion réussie !")
                return True
            else:
                logger.error("Échec connexion : Toujours sur la page de login")
                self.page.screenshot(path="logs/login_fail.png")
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
        
    def navigate_to_module(self, module_name="Orthographe"):
        logger.info(f"Navigation vers module: {module_name}")
        try:
            # Recherche du module dans le dashboard
            self.page.wait_for_selector(f"text={module_name}", timeout=15000)
            self.page.click(f"text={module_name}")
            self.page.wait_for_load_state("networkidle")
            
            # Clic sur Commencer/Continuer
            for btn_text in ["Lancer l'entraînement", "Continuer", "Commencer"]:
                try:
                    btn = self.page.wait_for_selector(f"text={btn_text}", timeout=5000)
                    if btn:
                        btn.click()
                        logger.info(f"Module {module_name} démarré.")
                        return True
                except:
                    continue
        except Exception as e:
            logger.warning(f"Impossible de démarrer {module_name}: {e}")
        return False

    def run_session(self):
        logger.info(f"Début session de farming ({CONFIG['SESSION_DURATION_MIN']} min)...")
        start_time = time.time()
        duration = CONFIG["SESSION_DURATION_MIN"] * 60
        
        while (time.time() - start_time) < duration:
            try:
                if not self.do_exercise():
                    time.sleep(5) # Attente si bloqué
            except Exception as e:
                logger.error(f"Erreur exercice: {e}")
                break
                
    def do_exercise(self):
        try:
            # Détection du texte de la question
            question_el = self.page.wait_for_selector(".question, .enonce, .sentence", timeout=10000)
            if not question_el: return False
            
            # Détection des options
            options = self.page.query_selector_all("button.choice, .option, [role='button']")
            if not options: return False

            # Choix IA
            best = self.ai.pick_best_answer(question_el.inner_text(), options)
            if best:
                time.sleep(random.uniform(1, 3)) # Simulation réflexion
                best.click()
                
                # Validation
                time.sleep(1)
                validate = self.page.query_selector("text=Valider, text=OK, .btn-validate")
                if validate: validate.click()
                
                time.sleep(2) # Attente feedback
                return True
        except:
            return False
        return False

# ==========================================
# 🚀 EXECUTION
# ==========================================
def run_bot():
    if CONFIG["EMAIL"] == "VOTRE_EMAIL@et.esiea.fr":
        logger.error("Veuillez configurer vos identifiants dans les variables d'environnement.")
        return

    with sync_playwright() as p:
        stealth = StealthDriver(p)
        page = stealth.start()
        
        login_mgr = LoginManager(page)
        if login_mgr.login():
            farmer = VoltaireFarmer(page)
            # Priorité Orthographe comme demandé
            for module in ["Orthographe", "Expression", "Courriels"]:
                if farmer.navigate_to_module(module):
                    farmer.run_session()
        
        stealth.stop()

if __name__ == "__main__":
    run_bot()
