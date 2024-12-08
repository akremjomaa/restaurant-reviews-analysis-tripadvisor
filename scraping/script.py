from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Configuration Selenium
CHROMEDRIVER_PATH = "chromedriver/chromedriver.exe"  
URL = "https://www.tripadvisor.fr/Restaurants-g187265-oa0-Lyon_Rhone_Auvergne_Rhone_Alpes.html"

def init_selenium_driver(chromedriver_path):
    """
    Initialise le driver Selenium avec Chrome.
    """
    options = Options()
    options.add_argument("--headless")  # Mode sans interface graphique
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

    service = Service(chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_html_with_selenium(url, driver):
    """
    Charge une page avec Selenium et retourne son contenu HTML.
    """
    driver.get(url)
    time.sleep(3)  # Attends que la page se charge complètement
    return driver.page_source

def scrape_first_restaurant(html):
    """
    Analyse le HTML pour extraire les informations du premier restaurant.
    """
    soup = BeautifulSoup(html, 'lxml')

    # Sélectionne le premier restaurant
    first_restaurant = soup.select_one('.restaurants-list-ListCell__cellContainer--2mpJS')

    if not first_restaurant:
        print("Aucun restaurant trouvé.")
        return None

    # Nom du restaurant
    name = first_restaurant.select_one('.restaurants-list-ListCell__restaurantName--2aSdo').text.strip()

    # Lien vers la page détaillée
    link = first_restaurant.select_one('.restaurants-list-ListCell__restaurantName--2aSdo').get('href')
    link = f"https://www.tripadvisor.fr{link}"

    # Note
    rating = first_restaurant.select_one('.restaurants-list-ListCell__rating--1h3a3 span')
    rating = rating.text.strip() if rating else "Non noté"

    # Nombre d'avis
    reviews_count = first_restaurant.select_one('.restaurants-list-ListCell__userReviewCount--2aFlV')
    reviews_count = reviews_count.text.strip() if reviews_count else "Aucun avis"

    # Retourne les informations
    return {
        "name": name,
        "link": link,
        "rating": rating,
        "reviews_count": reviews_count,
    }

def main():
    driver = init_selenium_driver(CHROMEDRIVER_PATH)
    try:
        print("Chargement de la page...")
        html = get_html_with_selenium(URL, driver)

        print("Extraction des informations...")
        restaurant = scrape_first_restaurant(html)

        if restaurant:
            print("Informations du premier restaurant :")
            print(restaurant)
        else:
            print("Aucun restaurant trouvé.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
