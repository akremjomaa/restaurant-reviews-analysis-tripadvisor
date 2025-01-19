import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import IsolationForest
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re

nltk.download('punkt')
nltk.download('stopwords')

# ---- Fonctions Utilitaires ----
def preprocess_text(text):
    text = text.lower()  
    text = re.sub(r'\W', ' ', text)  
    text = re.sub(r'\d', ' ', text)  
    tokens = word_tokenize(text)  
    stop_words = set(stopwords.words('french'))
    tokens = [word for word in tokens if word not in stop_words] 
    return ' '.join(tokens)

def apply_sentiment_to_reviews(df_reviews, sentiment_categories):
    sentiment_results = df_reviews['review_text'].apply(lambda x: detailed_sentiment_analysis(x, sentiment_categories))
    
    # Créer de nouvelles colonnes dans le DataFrame pour chaque catégorie de sentiment
    for category in sentiment_categories.keys():
        df_reviews[f'sentiment_{category}'] = sentiment_results.apply(lambda x: x.get(category, 'neutre'))
    
    return df_reviews

def compute_top_keywords(df, excluded_words=None, max_words=20):
    """
    Analyse de fréquence des mots-clés, avec possibilité d'exclure certains mots.
    """
    if excluded_words is None:
        excluded_words = []

    vectorizer = CountVectorizer(stop_words=stopwords.words('french'), max_features=100)  
    X = vectorizer.fit_transform(df['cleaned_review'])
    keywords = vectorizer.get_feature_names_out()
    keyword_counts = X.toarray().sum(axis=0)

    # Crée un DataFrame des mots-clés avec leur fréquence
    df_keywords = pd.DataFrame({'keyword': keywords, 'count': keyword_counts}).sort_values(by='count', ascending=False)

    # Filtrer les mots-clés exclus
    df_keywords = df_keywords[~df_keywords['keyword'].isin(excluded_words)]

    # Retourner les 20 mots les plus fréquents après filtrage
    return df_keywords.head(max_words)

def detailed_sentiment_analysis(text, sentiment_categories):
    sentiment_results = {}
    text_lower = text.lower()
    
    for category, keywords in sentiment_categories.items():
        has_positive = any(word in text_lower for word in keywords['positive'])
        has_negative = any(word in text_lower for word in keywords['negative'])
        
        if has_positive and not has_negative:
            sentiment_results[category] = 'positif'
        elif has_negative and not has_positive:
            sentiment_results[category] = 'négatif'
        elif has_positive and has_negative:
            sentiment_results[category] = 'mixte'
        else:
            sentiment_results[category] = 'neutre'
    
    return sentiment_results

# ---- Analyse des Avis ----
def nlp_analysis_interface(connection):
    st.title("🔍 Analyse NLP")

    # Charger les noms des restaurants pour le menu déroulant
    query_restaurants = """
        SELECT name
        FROM restaurants
        """
    restaurant_names = pd.read_sql_query(query_restaurants, connection)['name'].tolist()
    restaurant_names.insert(0, "Tous les restaurants")  # Ajouter une option pour tous les restaurants

    # Menu déroulant pour sélectionner un restaurant
    selected_restaurant = st.selectbox("Sélectionnez un restaurant :", restaurant_names)

    # Menu déroulant pour filtrer les avis en fonction du rating
    selected_rating_filter = st.selectbox("Sélectionnez le filtre de rating :", ["Tous les avis", "Avis avec rating <= 2", "Avis avec rating >= 4"])

    if selected_restaurant == "Tous les restaurants":
        query = """
            SELECT id_restaurant, rating, review_date, review_text
            FROM reviews
            WHERE review_text IS NOT NULL
        """
    else:
        query = f"""
            SELECT r.id_restaurant, review_text, rating, r.name
            FROM reviews rev
            JOIN restaurants r ON rev.id_restaurant = r.id_restaurant
            WHERE review_text IS NOT NULL AND r.name = '{selected_restaurant.replace("'", "''")}'
        """

    # Appliquer le filtre sur le rating
    if selected_rating_filter == "Avis avec rating <= 2":
        query += " AND rating <= 2"
    elif selected_rating_filter == "Avis avec rating >= 4":
        query += " AND rating >= 4"


    df_reviews = pd.read_sql_query(query, connection)

    # Vérifier si des avis existent pour le restaurant sélectionné
    if df_reviews.empty:
        st.warning(f"Aucun avis trouvé pour {selected_restaurant} avec le filtre sélectionné.")
        return

    # Détection des anomalies
    vectorizer = CountVectorizer(stop_words=stopwords.words('french'), max_features=20)
    X = vectorizer.fit_transform(df_reviews['review_text'])
    isolation_forest = IsolationForest(contamination=0.05, random_state=42)
    df_reviews['anomaly'] = isolation_forest.fit_predict(X.toarray())

    # Suppression des anomalies
    anomalies_removed = df_reviews[df_reviews['anomaly'] == -1]
    df_reviews = df_reviews[df_reviews['anomaly'] == 1]
    st.write(f"Nombre d'anomalies supprimées : {len(anomalies_removed)}")

    # Prétraitement des avis
    df_reviews['cleaned_review'] = df_reviews['review_text'].apply(preprocess_text)

    # Liste dynamique de mots exclus
    st.subheader("📊 Mots-Clés les Plus Fréquents")
    excluded_words = st.text_input("Entrez les mots-clés à exclure (séparés par des virgules) :", "")
    excluded_words_list = [word.strip().lower() for word in excluded_words.split(",") if word.strip()]

    # Analyse des mots-clés
    max_words = st.slider("Nombre de mots-clés à afficher", min_value=5, max_value=50, value=20)
    df_keywords = compute_top_keywords(df_reviews, excluded_words=excluded_words_list, max_words=max_words)
    fig_keywords = px.bar(df_keywords, x='keyword', y='count', title=f'Top {max_words} des mots-clés (après filtrage)', labels={'keyword': 'Mot-Clé', 'count': 'Fréquence'})
    st.plotly_chart(fig_keywords, use_container_width=True)

    # Analyse des sentiments
    st.subheader("😊 Analyse des Sentiments")
    sentiment_categories = {
        'satisfaction': {'positive': ['excellent', 'parfait', 'magnifique', 'impeccable', 'satisfait', 'exceptionnel', 'incroyable', 'formidable', 'agréable', 'génial'],
                        'negative': ['horrible', 'mauvais', 'décevant', 'inadmissible', 'désagréable', 'catastrophique', 'médiocre', 'nul', 'lamentable', 'affreux']},
        'food': {'positive': ['délicieux', 'savoureux', 'exquis', 'parfait', 'succulent', 'goûteux', 'appétissant', 'raffiné', 'succulent', 'irrésistible'],
                'negative': ['fade', 'insipide', 'mauvais', 'écoeurant', 'sec', 'immangeable', 'trop salé', 'trop sucré', 'brûlé', 'caoutchouteux']},
        'service': {'positive': ['rapide', 'sympathique', 'attentif', 'professionnel', 'chaleureux', 'accueillant', 'efficace', 'prévenant', 'discret', 'aimable'],
                    'negative': ['lent', 'impoli', 'médiocre', 'désorganisé', 'rude', 'arrogant', 'désagréable', 'incompétent', 'malhonnête', 'brusque']},
        'ambiance': {'positive': ['chaleureux', 'confortable', 'calme', 'agréable', 'cosy', 'intimiste', 'relaxant', 'charmant', 'lumineux', 'paisible'],
                    'negative': ['bruyant', 'froid', 'désagréable', 'sombre', 'oppressant', 'sale', 'désordonné', 'chaotique', 'déprimant', 'hostile']},
        'price': {'positive': ['abordable', 'raisonnable', 'correct', 'économique', 'juste', 'compétitif', 'accessible', 'avantageux', 'équitable', 'modéré'],
                'negative': ['cher', 'excessif', 'abusif', 'injustifié', 'hors de prix', 'exorbitant', 'démesuré', 'prohibitif', 'trop coûteux', 'inabordable']},
        'hygiene': {'positive': ['propre', 'soigné', 'impeccable', 'net', 'irréprochable', 'hygiénique', 'bien entretenu', 'aseptisé', 'nickel', 'brillant'],
                    'negative': ['sale', 'malpropre', 'négligé', 'dégueulasse', 'infect', 'insalubre', 'crasseux', 'malodorant', 'contaminé', 'délabré']}
    }

    # Appliquer l'analyse de sentiment
    df_reviews['sentiments'] = df_reviews['review_text'].apply(
        lambda x: detailed_sentiment_analysis(x, sentiment_categories)
    )

    # Empiler les résultats des sentiments pour chaque catégorie et les compter
    sentiment_summary = df_reviews['sentiments'].apply(pd.Series).stack().value_counts()

    # Filtrer les sentiments "neutres"
    sentiment_summary_filtered = sentiment_summary[sentiment_summary.index != 'neutre']

    # Générer le graphique de sentiment
    fig_sentiments = px.pie(values=sentiment_summary_filtered.values, names=sentiment_summary_filtered.index, title='Répartition des sentiments par catégorie (Excluant "Neutre")')
    st.plotly_chart(fig_sentiments, use_container_width=True)

    # Appliquer l'analyse des sentiments
    df_reviews_sentiments = apply_sentiment_to_reviews(df_reviews, sentiment_categories)
    df_reviews_sentiments = df_reviews_sentiments.drop(columns=['anomaly', 'cleaned_review', 'sentiments'])

    # Afficher le dataframe des avis avec les colonnes des sentiments
    st.subheader("📊 Résultats de l'Analyse des Sentiments")
    st.dataframe(df_reviews_sentiments)

    # Affichage des catégories de sentiments (optionnel)
    sentiment_summary = df_reviews[['sentiment_' + category for category in sentiment_categories.keys()]].apply(pd.Series.value_counts).T.fillna(0)
    st.subheader("📊 Résumé des Catégories de Sentiment")
    st.dataframe(sentiment_summary)

    # Extraction des aspects détectés
    st.subheader("🔍 Sélectionnez un Aspect")
    aspects = ['service', 'food', 'ambiance', 'price', 'hygiene']
    
    # Menu déroulant pour sélectionner l'aspect
    selected_aspect = st.selectbox("Choisissez un aspect :", aspects)

    # Filtrer les avis selon l'aspect sélectionné
    df_reviews['aspects_detected'] = df_reviews['review_text'].apply(
        lambda x: ', '.join([aspect for aspect in aspects if aspect in x.lower()])
    )

    # Filtrer les avis où l'aspect sélectionné est présent
    df_selected_aspect = df_reviews[df_reviews['aspects_detected'].str.contains(selected_aspect, case=False)]

    # Afficher les avis filtrés
    if not df_selected_aspect.empty:
        st.write(f"### Avis concernant l'aspect '{selected_aspect}'")
        st.dataframe(df_selected_aspect[['review_text', 'rating', 'aspects_detected']])
    else:
        st.write(f"Aucun avis trouvé pour l'aspect '{selected_aspect}'")
