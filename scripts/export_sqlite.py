"""
Exporte les tables de la base Kaggle « European Soccer Database »
(database.sqlite) en fichiers CSV dans le dossier data/.

Usage : python scripts/export_sqlite.py chemin/vers/database.sqlite
"""

import os
import sqlite3
import sys

import pandas as pd

TABLES = [
    "Country",
    "League",
    "Match",
    "Player",
    "Player_Attributes",
    "Team",
    "Team_Attributes",
]


def export(db_path, out_dir="data"):
    os.makedirs(out_dir, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        for table in TABLES:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            df.to_csv(os.path.join(out_dir, f"{table}.csv"), index=False)
            print(f"{table}: {len(df)} lignes")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    export(sys.argv[1])
