import requests
from bs4 import BeautifulSoup
import random
import re
import time
import logging


HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Configurer le logger
logging.basicConfig(
    level=logging.DEBUG,  # Niveau minimal de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format des logs
    handlers=[
        logging.FileHandler("scraper.log", mode="a", encoding="utf-8"),  # Enregistrer les logs dans un fichier
        logging.StreamHandler()  # Afficher les logs dans la console
    ]
)

# Créez un objet logger
logger = logging.getLogger(__name__)


def fetch_with_dynamic_wait(url, max_retries=5, base_delay=2, max_delay=60):
    """
    Récupère une page web avec gestion des erreurs HTTP et des pauses adaptatives.
    """
    for attempt in range(max_retries):
        try:
            HEADERS["User-Agent"] = random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            ])
            logger.info(f"Tentative {attempt + 1}/{max_retries} pour {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                logger.info(f"Succès pour {url}")
                return BeautifulSoup(response.text, 'lxml')

            elif response.status_code == 403:
                delay = min(base_delay * (2 ** attempt), max_delay) + random.uniform(0, 3)
                logger.warning(f"403 détecté. Pause de {delay:.2f} secondes.")
                time.sleep(delay)
            else:
                logger.error(f"Erreur HTTP {response.status_code}. Arrêt.")
                break

        except requests.exceptions.RequestException as e:
            delay = min(base_delay * (2 ** attempt), max_delay) + random.uniform(0, 3)
            logger.error(f"Erreur réseau : {e}. Pause de {delay:.2f} secondes.")
            time.sleep(delay)

    logger.critical(f"Échec après {max_retries} tentatives pour {url}")
    return None



def extract_manager_response(review):
    """
    Extrait la réponse du gérant à partir de la section d'un avis.
    :param review: L'objet BeautifulSoup correspondant à un avis.
    :return: La réponse du gérant si elle existe, sinon 'Aucune réponse'.
    """
    # Recherche du div contenant la réponse
    response_div = review.find("div", class_="csNQI PJ")
    if response_div:  
        response_text_span = response_div.find("span", class_="JguWG")
        if response_text_span: 
            return response_text_span.text.strip()
    return "Aucune réponse"

def scrape_modal_details(soup):
    """
    Scrape les informations dynamiques du modal de détails d'un restaurant.
    :param soup: L'objet BeautifulSoup de la page HTML.
    :return: Un dictionnaire contenant les détails du modal.
    """
    modal_data = {}

    # Recherche de toutes les sections du modal
    sections = soup.find_all("div", class_="Wf")
    for section in sections:
        # Titre de la section
        title = section.find("div")
        if title:
            title_text = title.text.strip()
            # Valeur associée à la section
            value = section.find_next_sibling("div")  # La valeur suit directement le titre
            value_text = value.text.strip() if value else "Non précisé"
            modal_data[title_text] = value_text

    return modal_data

def scrape_reviews(base_url):
    """
    Scrape tous les avis d'un restaurant avec gestion de la pagination.
    :param base_url: URL de la première page d'avis.
    :return: Liste des avis.
    """
    reviews_data = []
    current_url = base_url
    page_count = 1
    max_retries = 5  # Nombre maximum de tentatives pour une page
    base_delay = 5  # Délai de base en secondes pour la pause entre les tentatives
    max_delay = 60  # Délai maximum en secondes

    while current_url:
        logger.info(f"Scraping page {page_count}...")
        retries = 0  # Compteur de tentatives pour la page actuelle
        
        while retries < max_retries:
            try:
                response = requests.get(current_url, headers=HEADERS, timeout=10)
                
                if response.status_code == 200:  # Succès
                    logger.info(f"Page {page_count} récupérée avec succès.")
                    soup = BeautifulSoup(response.text, 'lxml')

                    # Scrape des avis sur la page actuelle
                    reviews = soup.find_all('div', class_='_c', attrs={'data-automation': 'reviewCard'})
                    for review in reviews:
                        try:
                            author = review.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
                            author = author.text.strip() if author else "Auteur inconnu"

                            contributions_span = review.find("span", class_="b")
                            contributions = int(contributions_span.text.strip()) if contributions_span else 0

                            rating_svg = review.find('svg', class_='UctUV')
                            rating = None
                            if rating_svg:
                                rating_title = rating_svg.find('title')
                                if rating_title:
                                    rating_match = re.search(r"([\d,\.]+) sur 5", rating_title.text)
                                    rating = float(rating_match.group(1).replace(",", ".")) if rating_match else None

                            review_title = review.find('div', class_='biGQs _P fiohW qWPrE ncFvv fOtGX')
                            review_title = review_title.text.strip() if review_title else "Titre non spécifié"

                            review_text = review.find('span', class_='JguWG')
                            review_text = review_text.text.strip() if review_text else "Texte non spécifié"

                            manager_response = extract_manager_response(review)

                            review_date = review.find('div', class_='neAPm')
                            review_date = review_date.find('div', class_='biGQs _P pZUbB ncFvv osNWb').text.strip() if review_date else "Date non spécifiée"

                            reviews_data.append({
                                "author": author,
                                "contributions": contributions,
                                "rating": rating,
                                "title": review_title,
                                "review_text": review_text,
                                "manager_response": manager_response,
                                "review_date": review_date,
                            })
                        except Exception as e:
                            logger.error(f"Erreur lors du scraping d'un avis : {e}")

                    # Trouver le lien vers la page suivante
                    next_button = soup.find('a', {'aria-label': 'Page suivante'})
                    if next_button and next_button.get('href'):
                        current_url = "https://www.tripadvisor.fr" + next_button['href']
                        page_count += 1
                    else:
                        logger.info("Aucune page suivante trouvée. Fin de la pagination.")
                        current_url = None

                    # Pause avant de passer à la page suivante
                    time.sleep(random.uniform(3, 7))
                    break  

                elif response.status_code == 403:  # Bloqué par le serveur
                    delay = min(base_delay * (2 ** retries), max_delay) + random.uniform(0, 3)
                    logger.warning(f"Code 403 détecté. Pause de {delay:.2f} secondes avant nouvelle tentative.")
                    time.sleep(delay)
                    retries += 1

                else:   # Autre erreur HTTP
                    logger.error(f"Erreur HTTP {response.status_code}. Arrêt du scraping pour cette page.")
                    retries += 1
                    break

            except requests.exceptions.RequestException as e:
                delay = min(base_delay * (2 ** retries), max_delay) + random.uniform(0, 3)
                logger.warning(f"Erreur réseau : {e}. Pause de {delay:.2f} secondes avant nouvelle tentative.")
                time.sleep(delay)
                retries += 1

        # Si les tentatives échouent après max_retries
        if retries >= max_retries:
            logger.error(f"Échec du scraping de la page {page_count} après {max_retries} tentatives.")
            break

    logger.info(f"Scraping terminé : {len(reviews_data)} avis extraits.")
    return reviews_data


def scrape_restaurant(url):
    """
    Scrape les informations détaillées d'un restaurant sur TripAdvisor.
    :param url: L'URL de la page du restaurant sur TripAdvisor.
    :return: Un dictionnaire contenant les informations extraites.
    """
    
    try:
        soup = fetch_with_dynamic_wait(url)
        if not soup:
            logger.error(f"Impossible de récupérer les données pour {url}")
            return None

        # Extraction des données principales

        name = soup.select_one('h1.biGQs._P.hzzSG.rRtyp')
        address = soup.select_one('span[data-automation="restaurantsMapLinkOnName"]')
        reviews_count_tag  = soup.select_one('span.OFtgC')
        rating_svg = soup.select_one('svg.UctUV[aria-labelledby]')
        rating = None
        if rating_svg:
            title = rating_svg.find('title')
        if title and "sur 5" in title.text:
            rating = float(title.text.split(" sur 5")[0].replace(",", "."))

        ranking_section = soup.select_one('span.ffHqI')

        name = name.text.strip() if name else None
        address = address.text.strip() if address else None

        if reviews_count_tag:
            reviews_count = int(reviews_count_tag.text.replace("avis", "").replace("\u202f", "").replace(",", "").strip())

        else :
            reviews_count = None
        if ranking_section:
            ranking_text = ranking_section.text.strip()
            # Classement (extrait uniquement le numéro après "Nº")
            ranking_match = re.search(r"Nº\s*(\d+)", ranking_text)
            ranking = int(ranking_match.group(1)) if ranking_match else None
            # Total de restaurants (extrait le numéro après "sur")
            total_match = re.search(r"sur\s*([\d\u202f,]+)", ranking_text)
            if total_match:
                total_restaurants = total_match.group(1).replace("\u202f", "").replace(",", "")
                total_restaurants = int(total_restaurants) if total_restaurants.isdigit() else None
            else:
                total_restaurants = None
        else:
            ranking = None
            total_restaurants = None
         # Vérification des données critiques et nouvelle tentative si nécessaire
        if not (name and address and reviews_count and rating and ranking):
            logger.warning("Données incomplètes, nouvelle tentative après pause.")
            time.sleep(random.uniform(5, 10))
            return scrape_restaurant(url) 

        specific_ratings = {}
        rating_sections = soup.select('div.YwaWb.u.f')
        for section in rating_sections:
            title = section.select_one('span.biGQs._P.pZUbB.biKBZ.hmDzD')
            svg_title = section.select_one('div.JSTna title')
            if title and svg_title:
                category = title.text.strip()
                rating_match = re.search(r"([\d,\.]+) sur 5", svg_title.text)
                specific_rating = float(rating_match.group(1).replace(",", ".")) if rating_match else None
                specific_ratings[category] = specific_rating
        
        # Scrape du modal des détails
        modal_data = scrape_modal_details(soup)
        # Scrape des avis
        reviews_data = scrape_reviews(url)

        return {
            "name": name,
            "address": address,
            "reviews_count": reviews_count,
            "rating": rating,
            "ranking": ranking,
            "total_restaurants": total_restaurants,
            **specific_ratings,  # Ajout dynamique des notes spécifiques
            **modal_data,  # Ajout des détails dynamiques
             "reviews": reviews_data,  # Ajout des avis
             "url": url,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur de connexion : {e}")
        return None


def scrape_restaurant_list(base_url, max_restaurants=15, min_reviews=900):
    """
    Scrape les URLs des restaurants ayant plus de 'min_reviews' avis sur TripAdvisor.
    :param base_url: URL de la liste des restaurants avec pagination.
    :param max_restaurants: Nombre maximum de restaurants à scraper.
    :param min_reviews: Nombre minimum d'avis requis pour inclure un restaurant.
    :return: Liste des URLs des restaurants.
    """
    restaurant_urls = []
    current_url = base_url
    page_count = 0

    while current_url and len(restaurant_urls) < max_restaurants:
        logger.info(f"Scraping restaurant list, page {page_count + 1}...")
        response = requests.get(current_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            logger.error(f"Erreur HTTP {response.status_code} sur {current_url}. Arrêt du scraping.")
            break

        soup = BeautifulSoup(response.text, 'lxml')
        restaurant_cards = soup.find_all('div', class_='tbrcR _T DxHsn TwZIp rrkMt nSZNd DALUy Re')

        for card in restaurant_cards:
            # Récupérer le nombre d'avis
            reviews_span = card.select_one('span.biGQs._P.pZUbB.osNWb > span.yyzcQ')
            if reviews_span:
                try:
                    reviews_count = int(reviews_span.text.replace("\u202f", "").replace(",", ""))
                except ValueError:
                    reviews_count = 0
            else:
                reviews_count = 0

            # Si le restaurant a assez d'avis, on récupère son URL
            if reviews_count >= min_reviews:
                link = card.find('a', class_='BMQDV _F Gv wSSLS SwZTJ FGwzt ukgoS')
                if link and link.get('href'):
                    restaurant_url = "https://www.tripadvisor.fr" + link['href']
                    restaurant_urls.append(restaurant_url)
                    logger.info(f"Restaurant trouvé : {restaurant_url} avec {reviews_count} avis.")
                    # Arrêter si on atteint le maximum
                    if len(restaurant_urls) >= max_restaurants:
                        break

        # Trouver le lien vers la page suivante
        next_button = soup.find('a', {'aria-label': 'Page suivante'})
        if next_button and next_button.get('href'):
            current_url = "https://www.tripadvisor.fr" + next_button['href']
            page_count += 1
            time.sleep(random.uniform(3, 7)) 
        else:
            logger.info("Aucune page suivante trouvée. Fin de la pagination.")
            current_url = None

    logger.info(f"Scraping terminé. {len(restaurant_urls)} restaurants trouvés.")
    return restaurant_urls