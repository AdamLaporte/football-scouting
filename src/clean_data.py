"""
Préparation des données de matchs.

- lit data/Match.csv (séparateur "," ou ";" détecté automatiquement) ;
- supprime les colonnes d'événements au format XML (goal, shoton, card...),
  inutilisées par l'analyse et qui alourdissent fortement le fichier ;
- écrit data/Match_clean.csv ;
- découpe les matchs par saison et par ligue dans
  data/match_annee/<saison>/league_<id>_season_<saison>.csv.

Usage : python -m src.clean_data   (depuis la racine du projet)
"""

import os

import pandas as pd

INPUT_FILE = "data/Match.csv"
OUTPUT_FILE = "data/Match_clean.csv"
SPLIT_DIR = "data/match_annee"

XML_COLUMNS = [
    "goal",
    "shoton",
    "shotoff",
    "foulcommit",
    "card",
    "cross",
    "corner",
    "possession",
]


def detect_separator(path):
    """Renvoie ';' ou ',' selon le séparateur utilisé dans l'en-tête."""
    with open(path, "r", encoding="utf-8") as f:
        header = f.readline()
    return ";" if header.count(";") > header.count(",") else ","


def clean_matches(input_file=INPUT_FILE, output_file=OUTPUT_FILE):
    """Charge les matchs, retire les colonnes XML et sauvegarde le résultat."""
    sep = detect_separator(input_file)
    matches = pd.read_csv(input_file, sep=sep, low_memory=False)
    matches = matches.drop(columns=XML_COLUMNS, errors="ignore")
    matches.to_csv(output_file, index=False)
    return matches


def split_by_season_and_league(matches, split_dir=SPLIT_DIR):
    """Écrit un fichier CSV par couple (saison, ligue)."""
    for (season, league_id), group in matches.groupby(["season", "league_id"]):
        season_dir = season.replace("/", "_")
        os.makedirs(os.path.join(split_dir, season_dir), exist_ok=True)
        path = os.path.join(
            split_dir,
            season_dir,
            f"league_{league_id}_season_{season_dir}.csv",
        )
        group.to_csv(path, index=False)


if __name__ == "__main__":
    df = clean_matches()
    split_by_season_and_league(df)
    print(f"{len(df)} matchs nettoyés -> {OUTPUT_FILE} et {SPLIT_DIR}/")
