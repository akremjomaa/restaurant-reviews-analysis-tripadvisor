import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from textblob import TextBlob
from sklearn.ensemble import IsolationForest
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import re

# Télécharger les ressources nécessaires de NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Connexion à la base de données
conn = sqlite3.connect("C:/Users/hp/Documents/GitHub/restaurant-reviews-analysis-tripadvisor/database/restaurants.db")

# Extraction des avis depuis la table reviews
query = "SELECT id_review, review_text, rating FROM reviews WHERE review_text IS NOT NULL;"
df_reviews = pd.read_sql_query(query, conn)
conn.close()

# ---- Détection des Anomalies ----
vectorizer = CountVectorizer(stop_words=stopwords.words('french'), max_features=20)
X = vectorizer.fit_transform(df_reviews['review_text'])
isolation_forest = IsolationForest(contamination=0.05, random_state=42)
anomaly_scores = isolation_forest.fit_predict(X.toarray())
df_reviews['anomaly'] = anomaly_scores

# Suppression des anomalies
anomalies_removed = df_reviews[df_reviews['anomaly'] == -1]
df_reviews = df_reviews[df_reviews['anomaly'] == 1]

# Nombre d'anomalies supprimées
print(f"Nombre d'anomalies supprimées : {len(anomalies_removed)}")

# ---- Préparation des groupes Low et High ----
group_low = df_reviews[df_reviews['rating'] <= 2.0]
group_high = df_reviews[df_reviews['rating'] > 3.5]

# Fonction de prétraitement du texte
def preprocess_text(text):
    text = text.lower()  # Convertir en minuscules
    text = re.sub(r'\W', ' ', text)  # Supprimer les caractères spéciaux
    text = re.sub(r'\d', ' ', text)  # Supprimer les chiffres
    tokens = word_tokenize(text)  # Tokenizer le texte
    stop_words = set(stopwords.words('french'))
    tokens = [word for word in tokens if word not in stop_words]  # Supprimer les stopwords
    return ' '.join(tokens)

# Appliquer le prétraitement
for group in [df_reviews, group_low, group_high]:
    group['cleaned_review'] = group['review_text'].apply(preprocess_text)

# ---- Analyse de Fréquence des Mots-Clés ----
def compute_top_keywords(df):
    vectorizer = CountVectorizer(stop_words=stopwords.words('french'), max_features=20)
    X = vectorizer.fit_transform(df['cleaned_review'])
    keywords = vectorizer.get_feature_names_out()
    keyword_counts = X.toarray().sum(axis=0)
    return pd.DataFrame({'keyword': keywords, 'count': keyword_counts}).sort_values(by='count', ascending=False)

# Calcul des mots-clés pour chaque groupe
df_keywords = compute_top_keywords(df_reviews)
df_keywords_low = compute_top_keywords(group_low)
df_keywords_high = compute_top_keywords(group_high)

# ---- Analyse de Sentiments ----
sentiment_categories = {
    'satisfaction': ['excellent', 'horrible', 'moyen', 'parfait'],
    'food': ['délicieux', 'fade', 'savoureux', 'insipide'],
    'service': ['rapide', 'lent', 'sympathique', 'impoli'],
    'ambiance': ['confortable', 'bruyant', 'chaleureux', 'froid'],
    'price': ['cher', 'abordable', 'raisonnable'],
    'hygiene': ['propre', 'sale'],
}

def detailed_sentiment_analysis(text):
    blob = TextBlob(text)
    sentiment_scores = {
        'polarity': blob.sentiment.polarity,
        'subjectivity': blob.sentiment.subjectivity
    }
    for category, keywords in sentiment_categories.items():
        sentiment_scores[category] = sum(1 for keyword in keywords if keyword in text.lower())
    return sentiment_scores

# Application de l'analyse des sentiments
for group in [df_reviews, group_low, group_high]:
    detailed_scores = group['review_text'].apply(detailed_sentiment_analysis)
    sentiment_df = pd.DataFrame(list(detailed_scores))
    group.reset_index(drop=True, inplace=True)
    sentiment_df.reset_index(drop=True, inplace=True)
    group[sentiment_df.columns] = sentiment_df

# ---- Extraction des Aspects ----
aspects = ['service', 'food', 'ambiance', 'price', 'menu']

def extract_aspects(text):
    text_lower = text.lower()
    detected_aspects = [aspect for aspect in aspects if aspect in text_lower]
    return ', '.join(detected_aspects)

# Application de l'extraction des aspects
for group in [df_reviews, group_low, group_high]:
    group['aspects_detected'] = group['review_text'].apply(extract_aspects)

# ---- Résultats ----
print("\nNombre d'anomalies supprimées :", len(anomalies_removed))

print("\nTop 20 des Mots-Clés (Low Ratings) :")
print(df_keywords_low)

print("\nTop 20 des Mots-Clés (High Ratings) :")
print(df_keywords_high)

print("\nTop 20 des Mots-Clés (Corpus Entier) :")
print(df_keywords)

print("\nAnalyse des Sentiments (Low Ratings) :")
print(group_low[['id_review', 'polarity', 'subjectivity'] + list(sentiment_categories.keys())].head())

print("\nAnalyse des Sentiments (High Ratings) :")
print(group_high[['id_review', 'polarity', 'subjectivity'] + list(sentiment_categories.keys())].head())

print("\nAnalyse des Sentiments (Corpus Entier) :")
print(df_reviews[['id_review', 'polarity', 'subjectivity'] + list(sentiment_categories.keys())].head())

print("\nAspects Détectés (Low Ratings) :")
print(group_low[['id_review', 'aspects_detected']].head())

print("\nAspects Détectés (High Ratings) :")
print(group_high[['id_review', 'aspects_detected']].head())

print("\nAspects Détectés (Corpus Entier) :")
print(df_reviews[['id_review', 'aspects_detected']].head())
