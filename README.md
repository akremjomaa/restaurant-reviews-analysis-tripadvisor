# L'Observatoire des Saveurs Lyonnaises

## Table des matières

- [Description](#description)
- [Installation](#installation)
- [Description des fonctionnalités de l'application](#description-des-fonctionnalité-application)
- [Contribution](#contribution)
- [Authors](#authors)  


## Description

Notre application extrait des données depuis une dizaine de restaurants lyonnais sur le site TripAdvisor, afin d'en fournir une présentation approfondie.

## Installation

Pour installer ce projet, suivez ces étapes :
1) Assurez vous d'avoir Python installé sur votre machine.

2) Clonez le dépôt :
```bash
git clone https://github.com/akremjomaa/restaurant-reviews-analysis-tripadvisor
```

3) Installez les dépendances :
```bash
pip install -r requirements.txt  
```

4) Configurez le PATH Python : 
```
set PYTHONPATH=Votre chemin\restaurant-reviews-analysis-tripadvisor\src
```
5) Lancez l'application :
```
streamlit run src/app/app.py
```

## Description des fonctionnalités de l'application

- Explorer les restaurants : Cet onglet permet de découvrir les données via des statistiques de base, tout en offrant la possibilité de télécharger les données affichées.
- Analyses NLP : Cet onglet propose à l'utilisateur d'explorer les mots-clés les plus fréquents dans les avis, une analyse des sentiments, ainsi qu'une liste des aspects détectés dans les avis.
- Carte interactive : Cet onglet permet de visualiser sur une carte les restaurants extraits, avec leurs noms, adresses, notes moyennes attribuées par les utilisateurs, ainsi qu'un résumé automatique généré par l'application.
- Ajouter un restaurant : Cette fonctionnalité permet de rechercher d'autres restaurants lyonnais disponibles sur TripAdvisor, puis d'afficher une carte des restaurants trouvés. En cliquant sur un point affiché, un bouton permet de scraper les données de ce restaurant et de l'ajouter à la base de données.

## Vous pouvez maintenant partir à la découverte des restaurants lyonnais ! 🦦


## Contribution
Les contributions sont les bienvenues ! Pour contribuer :
- Forkez le projet.
- Créez une branche pour votre fonctionnalité (git checkout -b feature/FeatureName).
- Validez vos modifications (git commit -m 'Description des modifications').
- Poussez sur la branche (git push origin feature/FeatureName).
- Ouvrez une Pull Request.

## Auteurs
Ce projet a été réalisé dans le cadre d'un projet pour le Master 2 SISE à l'Université Lumière Lyon 2 par :
- Antoine ORUEZABALA
- Bertrand KLEIN
- Akrem JOMAA
