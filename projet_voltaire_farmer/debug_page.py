import time
from playwright.sync_api import sync_playwright

def debug():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://compte.groupe-voltaire.fr/login")
        page.fill("input[placeholder='Identifiant']", "mabiala@et.esiea.fr")
        page.fill("input[placeholder='Mot de passe']", "Jesusestseigneur2024*")
        page.click("button:has-text('JE ME CONNECTE')")
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # Clic sur l'univers
        universes = page.query_selector_all("div")
        for u in universes:
            if "2025-2026" in u.inner_text() and "ACCÉDER" in u.inner_text():
                u.click()
                break
        
        time.sleep(10)
        print(f"URL après univers : {page.url}")
        page.screenshot(path="logs/debug_after_universe.png")
        
        # Liste tous les éléments cliquables
        elements = page.query_selector_all("a, button, [role='button']")
        print("Éléments cliquables :")
        for e in elements:
            try:
                text = e.inner_text().strip()
                if text: print(f"- {text}")
            except: pass
            
        browser.close()

if __name__ == "__main__":
    debug()
