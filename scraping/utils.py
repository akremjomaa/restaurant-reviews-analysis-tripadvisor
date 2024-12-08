from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import random
from selenium.webdriver.common.proxy import Proxy, ProxyType



def random_pause(min_time=5, max_time=10):
    time.sleep(random.uniform(min_time, max_time))

def scroll_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    random_pause(2, 5)  # Pause après le défilement
     
def get_html_with_selenium(url, driver):
    """
    Récupère le contenu HTML d'une page avec Selenium.
    """
    try:
        driver.get(url)
        random_pause()
        scroll_page(driver)
        return driver.page_source
    except Exception as e:
        print(f"Erreur avec Selenium : {e}")
        return None

def init_selenium_driver(chromedriver_path):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
    options.add_argument("--window-size=1920x1080")
    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def login_to_tripadvisor(driver, email, password):
    """
    Automatisation de la connexion à TripAdvisor.
    """
    try:
        # Aller à la page de connexion
        login_url = "https://www.tripadvisor.fr/Settings-captcha"
        driver.get(login_url)
        time.sleep(7)  # Attends le chargement de la page

        # Trouver le champ e-mail
        email_input = driver.find_element(By.ID, "regSignIn.email")
        email_input.clear()
        email_input.send_keys(email)

        # Trouver le champ mot de passe
        password_input = driver.find_element(By.ID, "regSignIn.password")
        password_input.clear()
        password_input.send_keys(password)

        # Soumettre le formulaire
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)  # Attends que la connexion soit complétée

        print("Connexion réussie.")
    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
