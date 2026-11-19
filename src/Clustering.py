import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import NearestNeighbors
from collections import Counter
import os


def analyze_players_and_plot():
    # Chargement des données
    df = pd.read_csv("data/Player_Attributes.csv", low_memory=False)
    players_info = pd.read_csv("data/Player.csv", low_memory=False)[
        ["player_fifa_api_id", "player_name"]
    ]

    # Nettoyage des données
    df = df.sort_values("date").drop_duplicates("player_api_id", keep="last")
    df = df[df["gk_handling"] < 30]
    df = df[df["gk_kicking"] < 30]
    df = df[df["gk_diving"] < 30]
    df = df[df["gk_positioning"] < 30]
    df = df[df["gk_reflexes"] < 30]

    df = df.dropna(
        subset=[
            "attacking_work_rate",
            "defensive_work_rate",
            "finishing",
            "shot_power",
            "long_shots",
            "positioning",
            "marking",
            "standing_tackle",
            "interceptions",
            "aggression",
        ]
    )

    # Encodage des work rates
    mapping = {"low": 0, "medium": 1, "high": 2}
    df["att_wr"] = df["attacking_work_rate"].map(mapping)
    df["def_wr"] = df["defensive_work_rate"].map(mapping)

    # Calcul des scores offensif et défensif
    df["offensive_score"] = df[
        ["finishing", "shot_power", "long_shots", "positioning"]
    ].mean(axis=1)
    df["defensive_score"] = df[
        ["marking", "standing_tackle", "interceptions", "aggression"]
    ].mean(axis=1)

    # Fonction pour assigner les postes en fonction de work rates
    def assign_position(row):
        if row["att_wr"] > row["def_wr"]:  # Attaquant
            return "Attaquant"
        elif row["att_wr"] < row["def_wr"]:  # Défenseur
            return "Défenseur"
        else:  # Milieu
            return "Milieu"

    df["position_estimee"] = df.apply(assign_position, axis=1)

    # Sélection des joueurs spécifiques
    ronaldo = df[df["player_fifa_api_id"] == 20801]
    messi = df[df["player_fifa_api_id"] == 158023]
    ramos = df[df["player_fifa_api_id"] == 155862]
    kante = df[df["player_fifa_api_id"] == 215914]
    autres = df[
        ~df["player_fifa_api_id"].isin([20801, 158023, 155862, 215914])
    ]

    # Graphique
    plt.figure(figsize=(8, 6))
    sns.scatterplot(
        data=autres,
        x="defensive_score",
        y="offensive_score",
        hue="position_estimee",
        palette="Set2",
        alpha=0.6,
        s=60,
    )

    # Ajout des joueurs spécifiques
    for player, name in zip(
        [ronaldo, ramos, kante, messi], ["Ronaldo", "Ramos", "Kanté", "Messi"]
    ):
        plt.scatter(
            player["defensive_score"],
            player["offensive_score"],
            color="red",
            s=120,
            edgecolor="black",
            label=name,
        )
        plt.text(
            player["defensive_score"].values[0] + 1,
            player["offensive_score"].values[0] + 1,
            name,
            fontsize=10,
            color="red",
            weight="bold",
        )

    plt.xlabel("Score Défensif")
    plt.ylabel("Score Offensif")
    plt.grid(True)
    plt.legend(title="Poste estimé")
    plt.tight_layout()

    # Sauvegarde de l'image
    os.makedirs("results/Clustering", exist_ok=True)
    image_path = "results/Clustering/player_analysis_plot.png"
    plt.savefig(image_path)

    # Fonction pour demander les attributs
    def valeur_attribut(attribut):
        valeur = -1
        while valeur < 0 or valeur > 99:
            print(attribut, " doit être entre 0 et 99.")
            valeur = float(input("Entrez une valeur entre 0 et 99 "))
        return valeur

    # Fonction pour trouver les joueurs similaires
    def find_similar_players(n):
        print("Entrez les attributs suivants : ")
        finishing = valeur_attribut("Finishing")
        shot_power = valeur_attribut("Shot Power")
        long_shots = valeur_attribut("Long Shots")
        positioning = valeur_attribut("Positioning")
        marking = valeur_attribut("Marking")
        standing_tackle = valeur_attribut("Standing Tackle")
        interceptions = valeur_attribut("Interceptions")
        aggression = valeur_attribut("Aggression")

        query = pd.DataFrame(
            {
                "finishing": [finishing],
                "shot_power": [shot_power],
                "long_shots": [long_shots],
                "positioning": [positioning],
                "marking": [marking],
                "standing_tackle": [standing_tackle],
                "interceptions": [interceptions],
                "aggression": [aggression],
            }
        )

        knn = NearestNeighbors(n_neighbors=n)
        knn.fit(
            df[
                [
                    "finishing",
                    "shot_power",
                    "long_shots",
                    "positioning",
                    "marking",
                    "standing_tackle",
                    "interceptions",
                    "aggression",
                ]
            ]
        )

        indices = knn.kneighbors(query)[1]

        data_similaires = []
        print("\nJoueurs similaires:")
        for i in range(n):
            idx = indices[0][i]
            player = df.iloc[idx]
            player_id = player["player_fifa_api_id"]
            player_name = players_info[
                players_info["player_fifa_api_id"] == player_id
            ]["player_name"].values[0]

            data_similaires.append(
                {
                    "Nom": player_name,
                    "Poste estimé": player["position_estimee"],
                    "Finishing": player["finishing"],
                    "Shot Power": player["shot_power"],
                    "Long Shots": player["long_shots"],
                    "Positioning": player["positioning"],
                    "Marking": player["marking"],
                    "Standing Tackle": player["standing_tackle"],
                    "Interceptions": player["interceptions"],
                    "Aggression": player["aggression"],
                }
            )

        df_similaires = pd.DataFrame(data_similaires)
        print(df_similaires)

        poste_joueur = estimer_poste_knn(df_similaires["Poste estimé"])
        print("\nLe poste probable du joueur est :", poste_joueur)

        # Sauvegarde des résultats dans un fichier texte
        results_path = "results/Clustering/player_analysis_results.txt"
        with open(results_path, "w", encoding="utf-8") as fichier:
            fichier.write(
                f"Le poste probable du joueur est : {poste_joueur}\n\n"
            )
            fichier.write("Stats du joueur demandé :\n")
            fichier.write(
                f"Finishing: {finishing}, Shot Power: {shot_power}, Long"
                f" Shots: {long_shots}, Positioning: {positioning}, "
                f"Marking: {marking}, Standing Tackle: {standing_tackle}, "
                f"Interceptions: {interceptions}, Aggression: {aggression}\n\n"
            )
            fichier.write("Joueurs similaires:\n")
            fichier.write(df_similaires.to_string(index=False))

        print("\nStats du joueur demandé :")
        print(
            f"Finishing: {finishing}, Shot Power: {shot_power}, Long "
            f"Shots: {long_shots}, Positioning: {positioning}, "
            f"Marking: {marking}, Standing Tackle: {standing_tackle}, "
            f"Interceptions: {interceptions}, Aggression: {aggression}"
        )

    def estimer_poste_knn(postes):
        poste_majoritaire = Counter(postes).most_common(1)[0][0]
        return poste_majoritaire

    df = df[df['player_fifa_api_id'] != 182521]  # sans Toni Kroos
    find_similar_players(5)


# Clusterisation des joueurs
if __name__ == "__main__":
    analyze_players_and_plot()
