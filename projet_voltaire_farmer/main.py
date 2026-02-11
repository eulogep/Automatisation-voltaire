import os
import json
import random
import time
import logging
import schedule
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ==========================================
# ⚙️ CONFIGURATION (REMPLISSEZ CECI)
#   → Pour la sécurité, les identifiants sont lus
#     depuis les variables d'environnement :
#     PROJET_VOLTAIRE_EMAIL / PROJET_VOLTAIRE_PASSWORD
# ==========================================
CONFIG = {
    "EMAIL": os.getenv("PROJET_VOLTAIRE_EMAIL", "VOTRE_EMAIL@et.esiea.fr"),
    "PASSWORD": os.getenv("PROJET_VOLTAIRE_PASSWORD", "VOTRE_MOT_DE_PASSE"),
    "TARGET_SCORE": 70,
    "SESSION_DURATION_MIN": 20,
    "HEADLESS": False,  # Mettre à True pour mode invisible (plus stealth)
    "DEBUG": True
}

# ==========================================
# 📊 LOGGING SETUP
# ==========================================
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
    """Simule une IA pour choisir les réponses (Heuristique simple)"""
    
    @staticmethod
    def analyze_text(text):
        """Extrait des mots clés pour comprendre le contexte"""
        # Logique simplifiée pour l'exemple
        keywords = ["accord", "conjugaison", "pluriel", "singulier", "genre"]
        found = [k for k in keywords if k in text.lower()]
        return found

    @staticmethod
    def pick_best_answer(question_text, options_elements):
        """
        Score les réponses probables.
        Stratégie : 
        1. Longueur du texte (souvent plus détaillé = plus correct).
        2. Présence de mots clés de la question.
        """
        if not options_elements:
            return None
            
        scored_options = []
        
        for option in options_elements:
            text = option.inner_text().strip()
            score = 0
            
            # Heuristique 1: Préférence les réponses plus longues (explications)
            score += len(text) * 0.1
            
            # Heuristique 2: Correspondance mot clé
            keywords = GrammarAI.analyze_text(question_text)
            for k in keywords:
                if k in text.lower():
                    score += 5
            
            # Heuristique 3: Éviter les réponses vides ou très courtes
            if len(text) < 2:
                score -= 10
                
            scored_options.append((score, option))
            
        # Trie par score décroissant
        scored_options.sort(key=lambda x: x[0], reverse=True)
        
        # Retourne le meilleur élément
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
        logger.info("Demarrage moteur Stealth (Playwright)...")
        
        # UA Rotation Pool (Simulé)
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ]
        
        self.browser = self.p.chromium.launch(
            headless=CONFIG["HEADLESS"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars"
            ]
        )
        
        self.context = self.browser.new_context(
            user_agent=random.choice(user_agents),
            viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
            locale="fr-FR"
        )
        
        # Injection de script anti-détection
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = self.context.new_page()
        self.page.set_default_timeout(15000) # 15s timeout max
        return self.page

    def stop(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        logger.info("Moteur arrete.")

    def human_delay(self, min_s=1.0, max_s=3.0):
        """Délai aléatoire pour simuler un humain"""
        delay = random.uniform(min_s, max_s)
        time.sleep(delay)

# ==========================================
# 🔐 MODULE: LOGIN MANAGER
# ==========================================
class LoginManager:
    def __init__(self, page):
        self.page = page

    def login(self):
        logger.info(f"Tentative de connexion: {CONFIG['EMAIL']}")
        try:
            self.page.goto("https://www.projet-voltaire.fr/", wait_until="domcontentloaded")
            
            # Recherche bouton connexion (Multi-selecteurs)
            selectors = [
                "text=Connexion",
                "a[href*='connexion']",
                ".btn-connexion",
                "[data-testid='login-button']"
            ]
            
            login_btn = self._find_element(selectors)
            if login_btn:
                login_btn.click()
                self.page.human_delay()
            else:
                # Parfois on est déjà redirigé
                pass

            # Remplissage formulaire
            self.page.fill("input[name='email'], input[type='email'], #email", CONFIG["EMAIL"])
            self.page.human_delay(0.5, 1.5)
            self.page.fill("input[name='password'], input[type='password'], #password", CONFIG["PASSWORD"])
            self.page.human_delay(0.5, 1.5)
            
            # Clic Submit
            submit_selectors = [
                "button[type='submit']",
                "text=Se connecter",
                ".btn-submit"
            ]
            submit_btn = self._find_element(submit_selectors)
            if submit_btn:
                submit_btn.click()
            
            # Vérification succès (attendre URL dashboard ou élément spécifique)
            self.page.wait_for_load_state("networkidle")
            
            if "dashboard" in self.page.url.lower() or "mon-parcours" in self.page.url.lower():
                logger.info("Connexion reussie !")
                self._screenshot("login_success")
                return True
            else:
                logger.error("Echec connexion (URL ou identifiants incorrects)")
                self._screenshot("login_fail")
                return False

        except Exception as e:
            logger.error(f"Erreur critique lors de la connexion: {e}")
            return False

    def _find_element(self, selectors):
        for selector in selectors:
            try:
                el = self.page.wait_for_selector(selector, timeout=3000)
                if el: return el
            except:
                continue
        return None

    def _screenshot(self, name):
        if not os.path.exists("screenshots"): os.makedirs("screenshots")
        self.page.screenshot(path=f"screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{name}.png")

# ==========================================
# 🧭 MODULE: NAVIGATOR & SOLVER
# ==========================================
class VoltaireFarmer:
    def __init__(self, page):
        self.page = page
        self.ai = GrammarAI()
        
    def navigate_to_module(self, module_name="Orthographe"):
        logger.info(f"Navigation vers module: {module_name}")
        try:
            # Sélecteurs génériques pour le menu
            link = self.page.wait_for_selector(f"text={module_name}", timeout=10000)
            if link:
                link.click()
                self.page.wait_for_load_state("networkidle")
                
                # Clic sur Commencer/Continuer
                start_btn = self._wait_for_any([
                    "text=Commencer",
                    "text=Continuer",
                    ".btn-start"
                ])
                if start_btn:
                    start_btn.click()
                    logger.info(f"Module {module_name} demarre.")
                    return True
        except Exception as e:
            logger.warning(f"Impossible de demarrer {module_name}: {e}")
        return False

    def run_session(self):
        logger.info("Debut session de farming (20 min)...")
        start_time = time.time()
        duration = CONFIG["SESSION_DURATION_MIN"] * 60
        exercises_count = 0
        
        while (time.time() - start_time) < duration:
            try:
                if self.do_exercise():
                    exercises_count += 1
                    logger.info(f"Exercice {exercises_count} termine.")
                else:
                    logger.warning("Exercice echoue ou bloque, retry...")
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Erreur boucle exercice: {e}")
                # Tenter de rafraîchir ou continuer
                break
                
        logger.info(f"Session terminee. {exercises_count} exercices effectues.")
        return exercises_count

    def do_exercise(self):
        try:
            # 1. Attendre que la question charge
            question_el = self.page.wait_for_selector(".question, .enonce, p[class*='texte']", timeout=10000)
            if not question_el: return False
            
            question_text = question_el.inner_text()
            
            # 2. Trouver les options de réponse
            # Note: Les sélecteurs doivent s'adapter à l'interface Voltaire
            options_selectors = [
                ".reponse",
                ".option",
                "button.choice",
                "label.choix",
                "[role='button']"
            ]
            
            options = []
            for s in options_selectors:
                found = self.page.query_selector_all(s)
                if found: 
                    options = found
                    break
            
            if not options:
                # Cas : Pas de boutons, peut-être saisie clavier ? (Non géré ici)
                return False

            # 3. IA Choice
            best_option = self.ai.pick_best_answer(question_text, options)
            
            if best_option:
                # Action humaine : Scroll vers l'élément
                best_option.scroll_into_view_if_needed()
                time.sleep(random.uniform(0.2, 0.5))
                best_option.click()
                
                # 4. Validation
                self.validate_exercise()
                return True
                
        except PlaywrightTimeoutError:
            return False
        except Exception as e:
            logger.debug(f"Erreur interne solveur: {e}")
            return False
        return False

    def validate_exercise(self):
        time.sleep(random.uniform(1.0, 2.5)) # Lecture de la réponse
        validate_selectors = [
            "text=Valider",
            "text=OK",
            "button[type='submit']",
            ".btn-valider"
        ]
        
        btn = self._wait_for_any(validate_selectors, timeout=3000)
        if btn:
            btn.click()
            # Attendre la correction/feedback
            time.sleep(random.uniform(2.0, 4.0))

    def _wait_for_any(self, selectors, timeout=5000):
        for s in selectors:
            try:
                return self.page.wait_for_selector(s, timeout=timeout)
            except:
                continue
        return None

# ==========================================
# 🚀 MAIN ORCHESTRATOR
# ==========================================
def run_bot():
    with sync_playwright() as p:
        # 1. Setup Driver
        stealth = StealthDriver(p)
        page = stealth.start()
        page.human_delay = stealth.human_delay # Patch method
        
        # 2. Login
        login_mgr = LoginManager(page)
        if not login_mgr.login():
            stealth.stop()
            return

        # 3. Farming Loop
        farmer = VoltaireFarmer(page)
        
        # Cycle: Orthographe -> Expression -> Courriels
        modules = ["Orthographe", "Expression", "Courriels"]
        
        for module in modules:
            if farmer.navigate_to_module(module):
                farmer.run_session()
                # Log progression
                progress = {
                    "timestamp": datetime.now().isoformat(),
                    "module": module,
                    "status": "completed"
                }
                os.makedirs("data", exist_ok=True)
                with open("data/progress.json", "a+") as f:
                    json.dump(progress, f)
                    f.write("\n")
            else:
                logger.info(f"Module {module} peut-être fini ou inaccessible.")
        
        logger.info("Tous les modules traites. Fermeture.")
        stealth.stop()

if __name__ == "__main__":
    # Mode immédiat
    if CONFIG["DEBUG"]:
        logger.info("MODE DEBUG: Lancement immediat")
        run_bot()
    
    # Mode Planning (Pro)
    # Décommentez ci-dessous pour activer le planning auto
    # else:
    #     logger.info("📅 MODE PLANNING: Attente créneaux (Mar/Jeu 14h)")
    #     schedule.every().tuesday.at("14:00").do(run_bot)
    #     schedule.every().thursday.at("14:00").do(run_bot)
    #     
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(60)
