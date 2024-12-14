import requests
from bs4 import BeautifulSoup
import random
import re
import json
import time


HEADERS = {
    "User-Agent": random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    ]),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def extract_manager_response(review):
    """
    Extrait la réponse du gérant à partir de la section d'un avis.
    :param review: L'objet BeautifulSoup correspondant à un avis.
    :return: La réponse du gérant si elle existe, sinon 'Aucune réponse'.
    """
    # Recherche du div contenant la réponse
    response_div = review.find("div", class_="csNQI PJ")
    if response_div:  # Vérifie si la div existe
        response_text_span = response_div.find("span", class_="JguWG")
        if response_text_span:  # Vérifie si le span existe
            return response_text_span.text.strip()
    # Si aucune réponse n'est trouvée
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
        title = section.find("div")  # Cherche le titre de manière générique
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

    while current_url :
        print(f"Scraping page {page_count}...")
        response = requests.get(current_url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code}. Arrêt du scraping.")
            break

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
                print(f"Erreur lors du scraping d'un avis : {e}")

        # Trouver le lien vers la page suivante
        next_button = soup.find('a', {'aria-label': 'Page suivante'})
        if next_button and next_button.get('href'):
            current_url = "https://www.tripadvisor.fr" + next_button['href']
            page_count += 1
        else:
            print("Aucune page suivante trouvée. Fin de la pagination.")
            current_url = None

        time.sleep(5)  # Pause pour éviter de surcharger le serveur

    print(f"Scraping terminé : {len(reviews_data)} avis extraits.")
    return reviews_data

def scrape_restaurant(url):
    """
    Scrape les informations détaillées d'un restaurant sur TripAdvisor.
    :param url: L'URL de la page du restaurant sur TripAdvisor.
    :return: Un dictionnaire contenant les informations extraites.
    """

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            print(f"Erreur HTTP {response.status_code} pour l'URL principale.")
            return None

        soup = BeautifulSoup(response.text, 'lxml')

        # Nom du restaurant
        name = soup.select_one('h1.biGQs._P.egaXP.rRtyp')
        name = name.text.strip() if name else None

        # adresse de restaurant
        address = soup.select_one("span.bTeln > button > span.biGQs._P.ttuOS > div.biGQs._P.pZUbB.hmDzD")
        address = address.text.strip() if address else None

        # Nombre d'avis
        reviews_count = soup.select_one('span.biGQs._P.fiohW.oXJmt')
        if reviews_count:
            reviews_count = reviews_count.text.replace("avis", "").strip()
            reviews_count = int(reviews_count.replace("\u202f", "").replace(",", ""))
        else:
            reviews_count = None

        # Note globale
        rating = soup.select_one('span.biGQs._P.fiohW.uuBRH')
        rating = rating.text.strip() if rating else None

        # Classement et total de restaurants
        ranking_section = soup.select_one('span.biGQs._P.pZUbB.hmDzD')
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
        }
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion : {e}")
        return None

def save_to_json(data, filename):
    """
    Sauvegarde les données dans un fichier JSON.
    :param data: Les données à sauvegarder.
    :param filename: Le nom du fichier.
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {filename}")

# Exemple d'URL
url = "https://www.tripadvisor.fr/Restaurant_Review-g187265-d23110895-Reviews-Frazarin-Lyon_Rhone_Auvergne_Rhone_Alpes.html"

restaurant_data = scrape_restaurant(url)

if restaurant_data:
    save_to_json(restaurant_data, "restaurant_data.json")