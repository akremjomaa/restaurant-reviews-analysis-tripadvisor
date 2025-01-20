
# L'Observatoire des Saveurs Lyonnaises

## Table des matières

- [Description](#description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Description des fonctionnalités de l'application](#description-des-fonctionnalités-de-lapplication)
- [Contribution](#contribution)
- [Authors](#auteurs)  

---

## Description

Notre application extrait des données depuis une dizaine de restaurants lyonnais sur le site TripAdvisor, afin d'en fournir une présentation approfondie. Ce projet inclut également des fonctionnalités avancées telles que l'analyse NLP et la visualisation interactive.

---

## Installation

Pour installer ce projet, suivez ces étapes :
1) Assurez-vous d'avoir Python installé sur votre machine.

2) Clonez le dépôt :
```bash
git clone https://github.com/akremjomaa/restaurant-reviews-analysis-tripadvisor
```

3) Installez les dépendances :
```bash
pip install -r requirements.txt  
```

4) Configurez le PATH Python : 
```bash
set PYTHONPATH=Votre chemin\restaurant-reviews-analysis-tripadvisor\src
```

---

## Configuration

1) **Obtenez une API Key de Mistral** :
   Pour utiliser certaines fonctionnalités basées sur des modèles de langage, vous devrez obtenir une clé API de Mistral.

2) **Créez un fichier `.env` à la racine du projet** :
   Ajoutez-y les informations suivantes :
   ```
   MISTRAL_API_KEY=VotreCleApiIci
   ```

3) **Assurez-vous que le fichier `.env` est bien configuré avant de lancer l'application.**

---

## Lancement de l'application

Lancez l'application via la commande suivante :
```bash
streamlit run src/app/app.py
```

---

## Description des fonctionnalités de l'application

- **Scraper les restaurants** : Extraire des informations détaillées sur les restaurants en utilisant des techniques de web scraping.
- **Explorer les restaurants** : Découvrez les données via des statistiques de base et téléchargez les données affichées.
- **Analyses NLP** : Analyse des mots-clés fréquents dans les avis, analyse des sentiments et extraction des aspects les plus mentionnés dans les avis.
- **Carte interactive** : Visualisez les restaurants extraits sur une carte avec leurs noms, adresses, notes moyennes, et un résumé automatique généré par l'application.
- **Résumé des avis** : Générer un résumé basé sur les avis laissés par les visiteurs en interrogeant un modèle de langage (LLM).
- **Ajouter un restaurant** : Recherche d'autres restaurants lyonnais sur TripAdvisor, affichage d'une carte interactive des résultats, et possibilité d'ajouter dynamiquement un restaurant à la base de données.

---

## Vous pouvez maintenant partir à la découverte des restaurants lyonnais ! 🦦

---

## Contribution

Les contributions sont les bienvenues ! Pour contribuer :
1. Forkez le projet.
2. Créez une branche pour votre fonctionnalité :
```bash
git checkout -b feature/FeatureName
```
3. Validez vos modifications :
```bash
git commit -m 'Description des modifications'
```
4. Poussez sur la branche :
```bash
git push origin feature/FeatureName
```
5. Ouvrez une Pull Request.

---

## Auteurs

Ce projet a été réalisé dans le cadre d'un projet pour le Master 2 SISE à l'Université Lumière Lyon 2 par :
- Antoine ORUEZABALA
- Bertrand KLEIN
- Akrem JOMAA
