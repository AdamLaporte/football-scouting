import time
import csv
import os
from .questions import (
    charger_donnees_matchs,
    trouver_plus_grosse_cote,
    afficher_resultat,
    function_bet_sans_panda,
    meilleur_joueur,
    meilleur_joueur_sans_panda,
    question1,
    question1_sans_pandas,
    equipe_avec_plus_defaites,
    equipe_avec_plus_defaitess,
)


def measure_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return end_time - start_time, result


def compare_times():
    os.makedirs("results/Time", exist_ok=True)
    results = []

    # Question 3 - Adam sans pandas
    fichier_matchs = "data/Match_clean.csv"
    fichier_equipes = "data/Team.csv"
    choix = "home"

    time_sans_panda, _ = measure_time(
        function_bet_sans_panda, fichier_matchs, fichier_equipes, choix
    )

    # Question 3 - Adam avec pandas
    def q3_adam_avec_panda():
        matchs_nommes = charger_donnees_matchs(
            fichier_matchs, fichier_equipes
        )
        match_max_cote = trouver_plus_grosse_cote(matchs_nommes, choix)
        reponsee = afficher_resultat(match_max_cote, choix)
        return reponsee

    time_avec_panda, _ = measure_time(q3_adam_avec_panda)

    results.append(("Question 3 - Adam", time_sans_panda, time_avec_panda))

    # Question 2 - Ilona
    type = "dribbling"
    time_avec_panda, _ = measure_time(meilleur_joueur, type)
    time_sans_panda, _ = measure_time(meilleur_joueur_sans_panda, type)

    results.append(
        ("Question 2 - Ilona", time_sans_panda, time_avec_panda)
    )

    # Question 1 - Anis
    time_avec_panda, _ = measure_time(question1)
    time_sans_panda, _ = measure_time(question1_sans_pandas)

    results.append(("Question 1 - Anis", time_sans_panda, time_avec_panda))

    # Question 1 - Aliaume
    match_file = "data/Match_clean.csv"
    team_file = "data/Team.csv"
    time_avec_panda, _ = measure_time(
        equipe_avec_plus_defaites, match_file, team_file
    )
    time_sans_panda, _ = measure_time(
        equipe_avec_plus_defaitess, match_file, team_file
    )

    results.append(
        ("Question 1 - Aliaume", time_sans_panda, time_avec_panda)
    )

    return results


def save_results_to_csv(
    results, filename="results/Time/comparaison_temps.csv"
):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Question", "Temps sans Pandas (s)", "Temps avec Pandas (s)"]
        )
        for result in results:
            writer.writerow(result)


if __name__ == "__main__":
    results = compare_times()
    save_results_to_csv(results)
