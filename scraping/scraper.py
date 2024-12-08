from bs4 import BeautifulSoup
from config import BASE_URL, MAX_RESTAURANTS, MIN_REVIEWS, CHROMEDRIVER_PATH
from script import scrape_first_restaurant
from utils import get_html_with_selenium, init_selenium_driver
import json

def parse_restaurant_details(url, driver):
    """
    Parse les détails supplémentaires d'un restaurant.
    """
    html = get_html_with_selenium(url, driver)
    if not html:
        return {}

    soup = BeautifulSoup(html, 'lxml')
    details = {}

    # Adresse
    address = soup.select_one('.fHibz')
    details['address'] = address.text.strip() if address else None

    # Notes spécifiques
    ratings = soup.select('.restaurants-detail-overview-cards-RatingsOverviewCard__ratingQuestionRow--1Ac2c')
    for rating in ratings:
        category = rating.select_one('.restaurants-detail-overview-cards-RatingsOverviewCard__ratingText--1P1LQ').text.strip()
        score = rating.select_one('.ui_bubble_rating').get('class')[1]
        score = int(score.split('_')[1]) / 10
        details[f"rating_{category}"] = score

    # Description
    description = soup.select_one('.restaurants-details-card-DesktopView__desktopAboutText--1j3e2')
    details['Infos pratiques'] = description.text.strip() if description else None

    # Autres détails (Cuisines, Repas, etc.)
    sections = soup.select('.restaurants-details-card-DetailsSectionOverviewCard__detailsSummary--evhlS')
    for section in sections:
        label = section.select_one('.restaurants-details-card-DetailsSectionOverviewCard__categoryTitle--2RJP_')
        value = section.select_one('.restaurants-details-card-DetailsSectionOverviewCard__tagText--1OH6h')
        if label and value:
            details[label.text.strip()] = ", ".join([v.text.strip() for v in section.select('.restaurants-details-card-DetailsSectionOverviewCard__tagText--1OH6h')])

    return details

def parse_restaurants(page_html, driver):
    """
    Parse les informations principales des restaurants sur une page.
    """
    soup = BeautifulSoup(page_html, 'lxml')
    restaurants = []

    for item in soup.select('.restaurants-list-ListCell__cellContainer--2mpJS'):
        try:
            name = item.select_one('.restaurants-list-ListCell__restaurantName--2aSdo').text.strip()
            link = item.select_one('.restaurants-list-ListCell__restaurantName--2aSdo').get('href')
            restaurant_url = f"https://www.tripadvisor.fr{link}"

            rating = item.select_one('.restaurants-list-ListCell__rating--1h3a3 span')
            rating = rating.text.strip() if rating else None

            reviews_count_text = item.select_one('.restaurants-list-ListCell__userReviewCount--2aFlV')
            reviews_count = int(reviews_count_text.text.strip().split()[0].replace('.', '')) if reviews_count_text else 0

            if reviews_count >= MIN_REVIEWS:
                details = parse_restaurant_details(restaurant_url, driver)
                restaurants.append({
                    "name": name,
                    "link": restaurant_url,
                    "rating": rating,
                    "reviews_count": reviews_count,
                    **details
                })
        except Exception as e:
            print(f"Erreur lors du parsing d'un restaurant : {e}")
            continue

    return restaurants

def save_to_json(data, filename):
    """
    Sauvegarde les données dans un fichier JSON.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    print(f"Données sauvegardées dans {filename}")

def main():

    driver = init_selenium_driver(CHROMEDRIVER_PATH)
        
    print("Démarrage du scraping...")
    driver = init_selenium_driver(CHROMEDRIVER_PATH)
    current_page = 0
    all_restaurants = []

    try:
        while len(all_restaurants) < MAX_RESTAURANTS:
            url = BASE_URL.format(page=current_page)
            print(f"Scraping page : {url}")
            page_html = get_html_with_selenium(url, driver)

            # # Vérifie si la page contient encore des résultats
            # soup = BeautifulSoup(page_html, 'lxml')
            # if not soup.select('.restaurants-list-ListCell__cellContainer--2mpJS'):
            #     print("Aucun résultat supplémentaire trouvé. Arrêt du scraping.")
            #     break

            restaurants = parse_restaurants(page_html, driver)
            all_restaurants.extend(restaurants)

            if len(all_restaurants) >= MAX_RESTAURANTS:
                break

            current_page += 30  # Passe à la page suivante

        all_restaurants = all_restaurants[:MAX_RESTAURANTS]
        save_to_json(all_restaurants, "data/top_restaurants.json")
    finally:
        driver.quit()
        print(f"Total des restaurants récupérés : {len(all_restaurants)}")

if __name__ == "__main__":
    main()
