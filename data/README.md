# Données

Les données ne sont pas versionnées dans ce dépôt (environ 360 Mo, au-delà des limites de GitHub).

## Source

[European Soccer Database](https://www.kaggle.com/datasets/hugomathien/soccer) (Hugo Mathien, Kaggle) :
plus de 25 000 matchs et 10 000 joueurs de 11 championnats européens, saisons 2008/2009 à 2015/2016,
avec les attributs des joueurs issus des jeux FIFA et les cotes de plusieurs bookmakers.

## Installation

1. Télécharger l'archive sur Kaggle (compte gratuit nécessaire) et extraire `database.sqlite`.
2. Exporter les tables en CSV dans ce dossier :

   ```bash
   python scripts/export_sqlite.py chemin/vers/database.sqlite
   ```

3. Nettoyer les matchs et générer le découpage par saison et par ligue :

   ```bash
   python -m src.clean_data
   ```

## Structure obtenue

```
data/
├── Country.csv
├── League.csv
├── Match.csv              # brut, avec les colonnes d'événements XML
├── Match_clean.csv        # généré : sans les colonnes XML
├── Player.csv
├── Player_Attributes.csv  # attributs FIFA des joueurs (plusieurs dates par joueur)
├── Team.csv
├── Team_Attributes.csv
└── match_annee/           # généré : un CSV par saison et par ligue
    └── 2008_2009/league_1_season_2008_2009.csv
```
