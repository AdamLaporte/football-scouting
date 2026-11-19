import os
from src.questions import (
    analyze_league_matches,
    process_largest_goal_difference,
    function_bet_sans_panda,
    charger_donnees_matchs,
    trouver_plus_grosse_cote,
    afficher_resultat,
    nb_moyen_but,
    meilleur_joueur,
    meilleur_joueur_sans_panda,
    team_with_most_goals_conceded,
    question1,
    question2,
    taux_de_victoire,
    question1_sans_pandas,
    afficher_boxplot_age_moyen,
    equipe_avec_plus_defaites,
    equipe_avec_plus_defaitess,
    equipe_plus_clean_sheets,
    moyenne_age_equipes,
)

from src.compare_time import (
    compare_times,
    save_results_to_csv,
)

from src.Clustering import analyze_players_and_plot

# --------------------------------------------------
# --------------------Questions---------------------
# --------------------------------------------------


os.makedirs("results/Questions", exist_ok=True)

# --------------QUESTION ADAM---------------

# Question 1 - Adam
if __name__ == "__main__":
    id_league = 21518  # Exemple : Liga BBVA
    match_file = "data/Match_clean.csv"
    team_file = "data/Team.csv"
    output_file = "stats_victoires_par_equipe.csv"

    results = analyze_league_matches(
        id_league, match_file, team_file, output_file
    )


# Question 2 - Adam
if __name__ == "__main__":
    data_path = "data/Match_clean.csv"
    team_path = "data/Team.csv"
    league_path = "data/League.csv"
    output_path2 = "largest_goal_difference.csv"

    final_table = process_largest_goal_difference(
        data_path, team_path, league_path, output_path2
    )

# Question 3 sans Panda - Adam

if __name__ == "__main__":
    fichier_matchs = "data/Match_clean.csv"
    fichier_equipes = "data/Team.csv"
    choix = "home"  # Remplacez par "away" ou "draw" selon vos besoins
    function_bet_sans_panda(fichier_matchs, fichier_equipes, choix)
    reponse = function_bet_sans_panda(
        fichier_matchs, fichier_equipes, choix
    )
    with open(
        "results/Questions/trouver_plus_grosse_cote_sans_panda.txt",
        "a",
        encoding="utf-8",
    ) as fichier:
        fichier.write(reponse)


# Question 3 avec Panda - Adam

if __name__ == "__main__":
    fichier_matchs = "data/Match_clean.csv"
    fichier_equipes = "data/Team.csv"
    matchs_nommes = charger_donnees_matchs(fichier_matchs, fichier_equipes)

    choix = "away"  # Remplacez par "away" ou "draw" selon vos besoins
    match_max_cote = trouver_plus_grosse_cote(matchs_nommes, choix)

    reponsee = afficher_resultat(match_max_cote, choix)
    with open(
        "results/Questions/trouver_plus_grosse_cote.txt",
        "w",
        encoding="utf-8",
    ) as fichier:
        fichier.write(reponsee + "\n" + "\n")


# --------------QUESTION Ilona---------------
# Q1 - Ilona

if __name__ == "__main__":
    id_league = "league_1"  # Exemple : Liga BBVA
    season = "2008_2009"  # Exemple : 2008_2009

    x = nb_moyen_but("league_1", "2008_2009")
    with open(
        "results/Questions/nb_moyen_but", "w", encoding="utf-8"
    ) as fichier:
        fichier.write(x)

# Q2 - Ilona avec panda
if __name__ == "__main__":
    type = "dribbling"
    y = meilleur_joueur(type)
    with open(
        "results/Questions/meilleur_joueur_dribble", "w", encoding="utf-8"
    ) as fichier:
        fichier.write(meilleur_joueur(type))

# Q2 - Ilona sans panda
if __name__ == "__main__":
    type = "dribbling"
    y = meilleur_joueur_sans_panda(type)
    with open(
        "results/Questions/meilleur_joueur_dribble_sans_panda",
        "w",
        encoding="utf-8",
    ) as fichier:
        fichier.write(meilleur_joueur_sans_panda(type))

# Q3 - Ilona
if __name__ == "__main__":
    type = "dribbling"
    y = team_with_most_goals_conceded()
    with open(
        "results/Questions/team_with_most_goals_conceded.csv", "w"
    ) as fichier:
        resultat = team_with_most_goals_conceded()
        fichier.write(resultat.to_csv(index=False))


# ------------------ QUESTION ANIS ------------------
# Question 1 - Anis avec pandas
if __name__ == "__main__":
    score_frequent = question1()
    with open(
        "results/Questions/Score_le_plus_fréquent.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            f"Score le plus fréquent : {score_frequent[0]} - "
            f"{score_frequent[1]} apparitions\n"
        )

# Question 1 - Anis sans pandas
if __name__ == "__main__":
    score_frequent = question1_sans_pandas()
    with open(
        "results/Questions/Score_le_plus_fréquent_sans_panda.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            f"Score le plus fréquent : {score_frequent[0]} - "
            f"{score_frequent[1]} apparitions\n"
        )

# Question 2 - Anis
if __name__ == "__main__":
    classement = question2()
    classement.to_csv(
        "results/Questions/Classement_ligue.csv",
        index=False,
        encoding="utf-8",
    )

# Question 3 - Anis
if __name__ == "__main__":
    saison = "2015/2016"
    championnat = "France Ligue 1"  # exemple : "France Ligue 1"
    stats_victoires = taux_de_victoire(saison, championnat)

    with open(
        "results/Questions/taux_de_victoire.txt", "w", encoding="utf-8"
    ) as f:
        f.write(f"Taux de victoire pour {championnat} en {saison} :\n")
        for type_victoire, taux in stats_victoires.items():
            f.write(f"{type_victoire} : {taux}\n")

# ------------------- QUESTION ALIAUME -------------------
# Question 1 - Aliaume
if __name__ == "__main__":
    match_file = "data/Match_clean.csv"
    team_file = "data/Team.csv"
    equipes = equipe_avec_plus_defaites(match_file, team_file)
    with open(
        "results/Questions/equipe_avec_plus_defaites.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(equipes)


# Question 1 sans panda - Aliaume
if __name__ == "__main__":
    match_file = "data/Match_clean.csv"
    team_file = "data/Team.csv"
    equipe = equipe_avec_plus_defaitess(match_file, team_file)
    with open(
        "results/Questions/equipe_avec_plus_defaitess_sans_panda.txt",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(equipe)

# Question 2 - Aliaume
if __name__ == "__main__":
    league_name = "England Premier League"
    saison = "2013/2014"
    clean_sheets = equipe_plus_clean_sheets(league_name, saison)
    clean_sheets.to_csv(
        "results/Questions/equipe_plus_clean_sheets.csv",
        index=False,
        encoding="utf-8",
    )


# Question 3 - Aliaume
if __name__ == "__main__":
    league_name = "England Premier League"
    saison = "2013/2014"
    age = moyenne_age_equipes(league_name, saison)
    age.to_csv("results/Questions/moyenne_age_equipes", index=False)

if __name__ == "__main__":
    league_name = "England Premier League"
    saison = "2013/2014"

    afficher_boxplot_age_moyen(league_name, saison)


# --------------------------------------------------
# ---------------Temps d'exécution------------------
# --------------------------------------------------

# Fonction pour comparer les temps d'exécution
if __name__ == "__main__":
    results = compare_times()
    save_results_to_csv(results)

# --------------------------------------------------
# ------------------Clustering----------------------
# --------------------------------------------------


# Clusterisation des joueurs
if __name__ == "__main__":
    analyze_players_and_plot()
