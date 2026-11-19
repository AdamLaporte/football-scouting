# Cellule 1 : Importer les bibliothèques et charger les données
import pandas as pd
import csv
import os
import matplotlib.pyplot as plt
import seaborn as sns


def process_largest_goal_difference(
    data_path, team_path, league_path, output_path2
):
    """
    Traite les matchs ayant la plus grande différence de buts et sauvegarde
    les résultats enrichis.

    Args:
        data_path (str): Chemin du fichier CSV des matchs.
        team_path (str): Chemin du fichier CSV des équipes.
        league_path (str): Chemin du fichier CSV des ligues.
        output_path2 (str): Nom du fichier de sortie à sauvegarder.

    Returns:
        pd.DataFrame: Tableau final contenant les matchs à plus grande différence
        de buts enrichis.
    """
    liga_bbva_matches = pd.read_csv(data_path, low_memory=False)

    liga_bbva_matches["goal_difference"] = abs(
        liga_bbva_matches["home_team_goal"]
        - liga_bbva_matches["away_team_goal"]
    )

    max_goal_diff_per_league = max(liga_bbva_matches["goal_difference"])

    largest_goal_diff_per_league = liga_bbva_matches[
        liga_bbva_matches["goal_difference"] == max_goal_diff_per_league
    ]

    largest_goal_diff_per_league = (
        largest_goal_diff_per_league.sort_values(
            by=["league_id", "goal_difference", "season"],
            ascending=[True, False, True],
        )
    )

    final_table = largest_goal_diff_per_league[
        [
            "league_id",
            "season",
            "home_team_api_id",
            "away_team_api_id",
            "home_team_goal",
            "away_team_goal",
            "goal_difference",
        ]
    ]

    teams = pd.read_csv(team_path, low_memory=False)
    leagues = pd.read_csv(league_path, low_memory=False)

    final_table = final_table.merge(
        teams,
        left_on="home_team_api_id",
        right_on="team_api_id",
        how="left",
    ).rename(columns={"team_long_name": "home_team_name"})

    final_table = final_table.merge(
        teams,
        left_on="away_team_api_id",
        right_on="team_api_id",
        how="left",
    ).rename(columns={"team_long_name": "away_team_name"})

    final_table = final_table.merge(
        leagues, left_on="league_id", right_on="id", how="left"
    ).rename(columns={"name": "league_name"})

    final_table = final_table[
        [
            "league_id",
            "league_name",
            "season",
            "home_team_name",
            "away_team_name",
            "home_team_goal",
            "away_team_goal",
            "goal_difference",
        ]
    ]

    final_table.to_csv("results/Questions/" + output_path2, index=False)

    return final_table


def analyze_league_matches(
    id_league, match_file, team_file, output_file=None
):
    """
    Analyse les matchs d'une ligue pour identifier l'équipe avec le plus de victoires
    par saison.

    Args:
        id_league (int): ID de la ligue à analyser.
        match_file (str): Chemin du fichier CSV des matchs.
        team_file (str): Chemin du fichier CSV des équipes.
        output_file (str, optional): Nom du fichier de sortie à sauvegarder.

    Returns:
        pd.DataFrame: Tableau des équipes ayant le plus de victoires par saison.
    """
    match_df = pd.read_csv(match_file, low_memory=False)

    league_matches = match_df[match_df["league_id"] == id_league]

    def get_winner(row):
        if row["home_team_goal"] > row["away_team_goal"]:
            return row["home_team_api_id"]
        elif row["home_team_goal"] < row["away_team_goal"]:
            return row["away_team_api_id"]
        else:
            return None

    league_matches["winner_team"] = league_matches.apply(
        get_winner, axis=1
    )
    league_matches = league_matches.dropna(subset=["winner_team"])
    league_matches["winner_team"] = league_matches["winner_team"].astype(
        int
    )

    victory_counts = (
        league_matches.groupby(["season", "winner_team"])
        .size()
        .reset_index(name="win_count")
    )

    top_teams_per_season = victory_counts.loc[
        victory_counts.groupby("season")["win_count"].idxmax()
    ]

    teams = pd.read_csv(team_file, low_memory=False)
    top_teams_with_names = top_teams_per_season.merge(
        teams[["team_api_id", "team_long_name"]],
        left_on="winner_team",
        right_on="team_api_id",
        how="left",
    )

    if output_file:
        top_teams_with_names.to_csv(
            "results/Questions/" + output_file, index=False
        )

    return top_teams_with_names[["season", "team_long_name", "win_count"]]


def charger_donnees_matchs(fichier_matchs, fichier_equipes):
    """
    Charge les fichiers de matchs et d’équipes, puis effectue les jointures
    pour associer les noms des équipes aux identifiants.

    Args:
        fichier_matchs (str): Chemin du fichier CSV des matchs.
        fichier_equipes (str): Chemin du fichier CSV des équipes.

    Returns:
        pd.DataFrame: Données des matchs enrichies avec les noms des équipes.
    """
    matchs = pd.read_csv(fichier_matchs, low_memory=False)
    equipes = pd.read_csv(fichier_equipes, low_memory=False)

    matchs = matchs[
        [
            "id",
            "league_id",
            "date",
            "home_team_api_id",
            "away_team_api_id",
            "home_team_goal",
            "away_team_goal",
            "B365H",
            "B365D",
            "B365A",
        ]
    ]

    matchs = (
        matchs.merge(
            equipes[["team_api_id", "team_long_name"]],
            left_on="home_team_api_id",
            right_on="team_api_id",
            how="left",
        )
        .rename(columns={"team_long_name": "home_team_name"})
        .drop(columns=["team_api_id"])
    )

    matchs = (
        matchs.merge(
            equipes[["team_api_id", "team_long_name"]],
            left_on="away_team_api_id",
            right_on="team_api_id",
            how="left",
        )
        .rename(columns={"team_long_name": "away_team_name"})
        .drop(columns=["team_api_id"])
    )

    return matchs


def trouver_plus_grosse_cote(matchs, choix):
    """
    Identifie le match avec la cote maximale selon le résultat souhaité.

    Args:
        matchs (pd.DataFrame): Données de matchs enrichies.
        choix (str): Résultat ciblé : "home", "away", ou "draw".

    Returns:
        pd.DataFrame: Match correspondant à la plus grande cote selon le choix.
    """
    if choix == "home":
        home_win = matchs[
            matchs["home_team_goal"] > matchs["away_team_goal"]
        ]
        max_b365h = home_win["B365H"].max()
        return home_win[home_win["B365H"] == max_b365h]

    elif choix == "away":
        away_win = matchs[
            matchs["away_team_goal"] > matchs["home_team_goal"]
        ]
        max_b365a = away_win["B365A"].max()
        return away_win[away_win["B365A"] == max_b365a]

    elif choix == "draw":
        draw = matchs[matchs["home_team_goal"] == matchs["away_team_goal"]]
        max_b365d = draw["B365D"].max()
        return draw[draw["B365D"] == max_b365d]

    else:
        raise ValueError(
            "Choix invalide. Utiliser 'home', 'away' ou 'draw'."
        )


def afficher_resultat(match, choix):
    """
    Retourne une phrase descriptive du match avec la plus grosse cote.

    Args:
        match (pd.DataFrame): Match contenant la cote maximale.
        choix (str): Résultat ciblé : "home", "away", ou "draw".

    Returns:
        str: Description du match le plus remarquable selon la cote.
    """
    if match.empty:
        return f"Aucun match avec une cote valide n'a été trouvé pour {choix}."

    match = match.iloc[0]
    date_match = match["date"].split(" ")[0]
    phrase = "avec la plus grosse cote remporté est le match"

    if choix == "home":
        return (
            f"Le match à domicile {phrase} du {date_match}, entre "
            f"{match['home_team_name']} et {match['away_team_name']} avec pour score : "
            f"{match['home_team_goal']} - {match['away_team_goal']}. "
            f"La cote remportée était de {match['B365H']}."
        )

    elif choix == "away":
        return (
            f"Le match à l'extérieur {phrase} du {date_match}, entre "
            f"{match['home_team_name']} et {match['away_team_name']} avec pour score : "
            f"{match['home_team_goal']} - {match['away_team_goal']}. "
            f"La cote remportée était de {match['B365A']}."
        )

    elif choix == "draw":
        return (
            f"Le match nul avec la plus grosse cote remporté est "
            f"le match du {date_match}, entre "
            f"{match['home_team_name']} et {match['away_team_name']} avec pour score : "
            f"{match['home_team_goal']} - {match['away_team_goal']}. "
            f"La cote remportée était de {match['B365D']}."
        )


def lire_csv(fichier):
    """
    Lit un fichier CSV et retourne une liste de dictionnaires.

    Args:
        fichier (str): Chemin du fichier CSV.

    Returns:
        list[dict]: Contenu du fichier.
    """
    with open(fichier, mode="r", encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        return list(lecteur)


def ecrire_csv(fichier, donnees, champs):
    """
    Écrit un fichier CSV dans le dossier `results/Questions` avec les données fournies.

    Args:
        fichier (str): Nom du fichier de sortie.
        donnees (list[dict]): Données à écrire.
        champs (list[str]): Liste des champs/colonnes.
    """
    dossier = os.path.join(os.getcwd(), "results/Questions")
    os.makedirs(dossier, exist_ok=True)
    chemin_complet = os.path.join(dossier, fichier)

    with open(chemin_complet, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=champs)
        writer.writeheader()
        writer.writerows(donnees)


def fusion_avec_equipe(donnees_matchs, equipes, cle_match, nom_colonne):
    """
    Associe à chaque match le nom de l’équipe en fonction d’une clé API.

    Args:
        donnees_matchs (list[dict]): Liste de matchs.
        equipes (list[dict]): Liste des équipes.
        cle_match (str): Nom de la clé API d'équipe dans les matchs.
        nom_colonne (str): Nom de la nouvelle colonne contenant le nom de l’équipe.

    Returns:
        list[dict]: Matchs enrichis du nom de l’équipe.
    """
    equipe_dict = {
        equipe["team_api_id"]: equipe["team_long_name"]
        for equipe in equipes
    }
    for match in donnees_matchs:
        match[nom_colonne] = equipe_dict.get(match[cle_match], "Inconnu")
    return donnees_matchs


def filtrer_et_trouver_max(donnees, condition, colonne_cote):
    """
    Filtre une liste de dictionnaires représentant des matchs en fonction
    d'une condition donnée, puis retourne ceux avec la cote maximale
    dans une colonne spécifique.

    Args:
        donnees (list[dict]): Liste des matchs à analyser.
        condition (function): Fonction booléenne qui détermine si un match est retenu.
        colonne_cote (str): Clé du dictionnaire correspondant à la cote à comparer.

    Returns:
        list[dict]: Liste des matchs ayant la cote maximale parmi ceux filtrés.
    """
    filtrés = [
        match
        for match in donnees
        if condition(match) and match[colonne_cote]
    ]

    cotes = [
        float(match[colonne_cote])
        for match in filtrés
        if match[colonne_cote].strip()
    ]

    if not cotes:
        return []

    max_cote = max(cotes)
    return [
        match
        for match in filtrés
        if float(match[colonne_cote]) == max_cote
    ]


def afficher_plus_grosse_cote(matchs_nommes, choix):
    """
    Retourne une chaîne descriptive du match avec la plus grosse cote gagnante,
    selon un type de résultat donné : victoire domicile, extérieur ou match nul.

    Args:
        matchs_nommes (list[dict]): Liste de matchs incluant les noms d'équipes.
        choix (str): Type de match à considérer : 'home', 'away' ou 'draw'.

    Returns:
        str: Description du match correspondant ou message d'erreur.
    """
    choix = choix.strip().lower()

    if choix == "home":
        home_win = filtrer_et_trouver_max(
            matchs_nommes,
            lambda m: int(m["home_team_goal"]) > int(m["away_team_goal"]),
            "B365H",
        )

        if home_win:
            match = home_win[0]
            date_match = match["date"].split(" ")[0]
            return (
                f"Le match à domicile avec la plus grosse cote remporté "
                f"est le match du {date_match}, "
                f"entre {match['home_team_name']} et "
                f"{match['away_team_name']} avec pour score : "
                f"{match['home_team_goal']} - {match['away_team_goal']}. "
                f"La cote remportée était de {match['B365H']}."
            )
        else:
            return "Aucun match à domicile valide n'a été trouvé."

    elif choix == "away":
        away_win = filtrer_et_trouver_max(
            matchs_nommes,
            lambda m: int(m["away_team_goal"]) > int(m["home_team_goal"]),
            "B365A",
        )

        if away_win:
            match = away_win[0]
            date_match = match["date"].split(" ")[0]
            return (
                f"Le match à l'extérieur avec la plus grosse cote "
                f"remporté est le match du {date_match}, "
                f"entre {match['home_team_name']} et "
                f"{match['away_team_name']} avec pour score : "
                f"{match['home_team_goal']} - {match['away_team_goal']}. "
                f"La cote remportée était de {match['B365A']}."
            )
        else:
            return "Aucun match à l'extérieur avec une cote valide n'a été trouvé"

    elif choix == "draw":
        draw = filtrer_et_trouver_max(
            matchs_nommes,
            lambda m: int(m["home_team_goal"]) == int(m["away_team_goal"]),
            "B365D",
        )
        if draw:
            match = draw[0]
            date_match = match["date"].split(" ")[0]
            return (
                f"Le match nul avec la plus grosse cote "
                f"remporté est le match du {date_match}, "
                f"entre {match['home_team_name']} et "
                f"{match['away_team_name']} avec pour score : "
                f"{match['home_team_goal']} - {match['away_team_goal']}. "
                f"La cote remportée était de {match['B365D']}."
            )
        else:
            return "Aucun match nul avec une cote valide n'a été trouvé."

    else:
        return "Choix invalide. Veuillez entrer 'home', 'away' ou 'draw'."


def function_bet_sans_panda(fichier_matchs, fichier_equipes, choix):
    """
    Fonction principale qui charge les données de matchs et d'équipes depuis
    des fichiers CSV, les fusionne, puis affiche le match avec la plus grosse
    cote gagnée selon un critère spécifié.

    Args:
        fichier_matchs (str): Chemin vers le fichier CSV contenant les matchs.
        fichier_equipes (str): Chemin vers le fichier CSV contenant les équipes.
        choix (str): Type de match à analyser : 'home', 'away' ou 'draw'.

    Returns:
        str: Résultat formaté du match avec la plus grosse cote.
    """
    matchs = lire_csv(fichier_matchs)
    equipes = lire_csv(fichier_equipes)

    colonnes_utiles = [
        "id",
        "league_id",
        "date",
        "home_team_api_id",
        "away_team_api_id",
        "home_team_goal",
        "away_team_goal",
        "B365H",
        "B365D",
        "B365A",
    ]

    matchs_filtrés = [
        {col: match[col] for col in colonnes_utiles} for match in matchs
    ]

    matchs_nommes = fusion_avec_equipe(
        matchs_filtrés, equipes, "home_team_api_id", "home_team_name"
    )
    matchs_nommes = fusion_avec_equipe(
        matchs_nommes, equipes, "away_team_api_id", "away_team_name"
    )

    return afficher_plus_grosse_cote(matchs_nommes, choix)


def nb_moyen_but(id_league, season):
    """
    Calcule le nombre moyen de buts par match pour une saison et une ligue données.

    Args:
        id_league (str): Identifiant de la ligue (e.g., 'league_1').
        season (str): Saison au format 'YYYY_YYYY' (e.g., '2008_2009').

    Returns:
        str: Résumé du nombre moyen de buts par match pour la saison et la
        ligue spécifiées,
             ainsi qu'une moyenne globale (identique ici car une seule
             saison/ligue est analysée).
    """
    df = pd.read_csv(f"data/match_annee/{season}/league_1_season_{season}.csv",
                     low_memory=False)

    total_buts_home = df["home_team_goal"].sum()
    total_buts_away = df["away_team_goal"].sum()
    total_buts = total_buts_home + total_buts_away
    total_matchs = df.shape[0]
    moyen_buts = total_buts / total_matchs

    return (
        f"Le nombre moyen de buts par match (saison {season} et "
        f"league {id_league}) est de : {moyen_buts}\n"
        f"Le nombre moyen de buts par match (saisons et ligues "
        f"confondues) est de : {moyen_buts}"
    )


def meilleur_joueur_sans_panda(attribut):
    """
    Identifie le ou les meilleurs joueurs pour un attribut donné sans utiliser Pandas.

    Args:
        attribut (str): Nom de l'attribut à évaluer (e.g., 'overall_rating').

    Returns:
        str: Nom(s) du ou des joueurs ayant obtenu la meilleure note pour cet attribut.
    """

    def lire_csv(fichier):
        with open(fichier, encoding="utf-8") as f:
            lecteur = csv.DictReader(f)
            return list(lecteur)

    player_attributes = lire_csv("data/Player_Attributes.csv")
    players = lire_csv("data/Player.csv")

    def meilleur_joueurs(attribut):
        attribut = attribut.strip().lower()

        if attribut not in player_attributes[0]:
            print(f"L'attribut '{attribut}' n'existe pas.")
            print(
                "Colonnes disponibles :", list(player_attributes[0].keys())
            )
            return

        max_val = None
        meilleurs_ids = []

        for ligne in player_attributes:
            valeur = ligne.get(attribut, "")
            try:
                valeur = float(valeur)
            except ValueError:
                continue

            if max_val is None or valeur > max_val:
                max_val = valeur
                meilleurs_ids = [ligne["player_api_id"]]
            elif valeur == max_val:
                meilleurs_ids.append(ligne["player_api_id"])

        noms = set()
        for joueur in players:
            if joueur["player_api_id"] in meilleurs_ids:
                noms.add(joueur.get("player_name", "Nom inconnu"))

        noms_str = ", ".join(noms)
        return (f"Meilleur(s) joueur(s) pour '{attribut}' : {noms_str} "
                f"avec une note de {max_val}.")

    return meilleur_joueurs(attribut)


def meilleur_joueur(attribut):
    """
    Identifie le ou les meilleurs joueurs pour un attribut donné en utilisant Pandas.

    Args:
        attribut (str): Nom de l'attribut à évaluer.

    Returns:
        str: Nom(s) du ou des joueurs ayant obtenu la note maximale pour cet attribut.
    """
    df1 = pd.read_csv("data/Player_Attributes.csv", low_memory=False)
    df2 = pd.read_csv("data/Player.csv", low_memory=False)
    attribut = attribut.strip().lower()

    if attribut not in df1.columns:
        print(f"L'attribut '{attribut}' n'existe pas.")
        print("Colonnes disponibles :", df1.columns.tolist())
        return

    valeur_max = df1[attribut].max()
    ids_max = df1.loc[df1[attribut] == valeur_max, "player_api_id"]
    noms_max = df2.loc[
        df2["player_api_id"].isin(ids_max), "player_name"
    ].unique()
    noms_str = ", ".join(noms_max)

    return (f"Meilleur(s) joueur(s) pour '{attribut}' : {noms_str} "
            f"avec une note de {valeur_max}.")


def team_with_most_goals_conceded():
    """
    Détermine, pour chaque saison, l'équipe ayant encaissé le plus de buts.

    Returns:
        DataFrame: Tableau contenant la saison, le nom de l’équipe,
        et le total de buts encaissés.
    """
    df_match = pd.read_csv("data/Match_clean.csv", low_memory=False)
    df_team = pd.read_csv("data/Team.csv", low_memory=False)

    home_conceded = df_match[
        ["season", "away_team_api_id", "home_team_goal"]
    ].copy()
    home_conceded.columns = ["season", "team_api_id", "goals_conceded"]

    away_conceded = df_match[
        ["season", "home_team_api_id", "away_team_goal"]
    ].copy()
    away_conceded.columns = ["season", "team_api_id", "goals_conceded"]

    conceded = pd.concat([home_conceded, away_conceded])
    total_conceded = (
        conceded.groupby(["season", "team_api_id"])["goals_conceded"]
        .sum()
        .reset_index()
    )
    max_conceded = total_conceded.loc[
        total_conceded.groupby("season")["goals_conceded"].idxmax()
    ]

    resultat_final = pd.merge(
        max_conceded,
        df_team[["team_api_id", "team_long_name"]],
        on="team_api_id",
        how="left",
    )
    resultat_final = resultat_final[
        ["season", "team_long_name", "goals_conceded"]
    ]

    return resultat_final


def question1():
    """
    Cette fonction analyse les données de match pour déterminer
    le score le plus fréquent entre les équipes
    à domicile et à l'extérieur où les buts sont égaux (matchs nuls).

    Elle charge les données depuis le fichier "Match_clean.csv" et identifie
    le score le plus fréquent parmi les matchs nuls.

    Retourne :
        tuple : Le score le plus fréquent et le nombre de fois
        qu'il est survenu sous forme de tuple (score, fréquence).
    """
    df = pd.read_csv("data/Match_clean.csv", low_memory=False)

    dom = df["home_team_goal"]
    ext = df["away_team_goal"]

    dict_scores = {
        "0-0": 0,
        "1-1": 0,
        "2-2": 0,
        "3-3": 0,
        "4-4": 0,
        "5-5": 0,
        "6-6": 0,
    }
    for x in range(len(dom)):
        if pd.notna(dom[x]) and dom[x] == ext[x]:
            score = f"{int(dom[x])}-{int(ext[x])}"
            if score in dict_scores:
                dict_scores[score] += 1

    max_value = max(dict_scores.values())
    max_couples = [
        (k, v) for k, v in dict_scores.items() if v == max_value
    ]
    max_couple = max_couples[0]

    return max_couple


# ---------------------- QUESTION 1 SANS PANDA----------------------


def question1_sans_pandas():
    """
    Cette fonction analyse les données de match pour déterminer
    le score le plus fréquent entre les équipes
    à domicile et à l'extérieur où les buts sont égaux (matchs nuls).

    Cette version de la fonction ne dépend pas de pandas, mais
    utilise la lecture du fichier CSV avec le module csv.

    Retourne :
        tuple : Le score le plus fréquent et le nombre de fois qu'il
        est survenu sous forme de tuple (score, fréquence).
    """
    dict_scores = {
        "0-0": 0,
        "1-1": 0,
        "2-2": 0,
        "3-3": 0,
        "4-4": 0,
        "5-5": 0,
        "6-6": 0,
    }

    with open("data/Match_clean.csv", mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            home = row["home_team_goal"]
            away = row["away_team_goal"]

            # Vérifier que les deux valeurs ne sont pas vides ou nulles
            if home != "" and away != "":
                if home == away:
                    score = f"{home}-{away}"
                    if score in dict_scores:
                        dict_scores[score] += 1

    # Trouver le score le plus fréquent
    max_value = max(dict_scores.values())
    max_couples = [
        (k, v) for k, v in dict_scores.items() if v == max_value
    ]
    max_couple = max_couples[0]

    return max_couple


# ---------------------- QUESTION 2 ----------------------


def question2():
    """
    Cette fonction calcule le classement des équipes de la saison
    2015/2016 du championnat "England Premier League",
    en tenant compte des buts marqués, des buts encaissés et des résultats des matchs.

    Elle retourne un DataFrame contenant le classement avec les colonnes suivantes :
        - Equipe : Nom de l'équipe
        - Match Joués : Nombre de matchs joués
        - Victoire : Nombre de victoires
        - Nul : Nombre de matchs nuls
        - Défaite : Nombre de défaites
        - Buts Pour : Nombre de buts marqués
        - Buts Contre : Nombre de buts encaissés
        - Points : Nombre de points obtenus
        - Différence : Différence entre buts marqués et encaissés.
    """
    df = pd.read_csv("data/Match_clean.csv", low_memory=False)
    leag = pd.read_csv("data/League.csv", low_memory=False)
    team = pd.read_csv("data/Team.csv", low_memory=False)

    id_league = leag.loc[
        leag["name"] == "England Premier League", "id"
    ].values[0]
    df_filtre = df[
        (df["season"] == "2015/2016") & (df["league_id"] == id_league)
    ]
    df_filtre = df_filtre[
        [
            "home_team_api_id",
            "away_team_api_id",
            "home_team_goal",
            "away_team_goal",
        ]
    ]

    classement = {}

    for _, match in df_filtre.iterrows():
        dom, ext = match["home_team_api_id"], match["away_team_api_id"]
        buts_dom, buts_ext = (
            match["home_team_goal"],
            match["away_team_goal"],
        )

        for equipe in [dom, ext]:
            if equipe not in classement:
                classement[equipe] = {
                    "Match Joués": 0,
                    "Victoire": 0,
                    "Nul": 0,
                    "Défaite": 0,
                    "Buts Pour": 0,
                    "Buts Contre": 0,
                    "Points": 0,
                }

        classement[dom]["Match Joués"] += 1
        classement[ext]["Match Joués"] += 1
        classement[dom]["Buts Pour"] += buts_dom
        classement[ext]["Buts Pour"] += buts_ext
        classement[dom]["Buts Contre"] += buts_ext
        classement[ext]["Buts Contre"] += buts_dom

        if buts_dom > buts_ext:
            classement[dom]["Victoire"] += 1
            classement[dom]["Points"] += 3
            classement[ext]["Défaite"] += 1
        elif buts_dom < buts_ext:
            classement[ext]["Victoire"] += 1
            classement[ext]["Points"] += 3
            classement[dom]["Défaite"] += 1
        else:
            classement[dom]["Nul"] += 1
            classement[ext]["Nul"] += 1
            classement[dom]["Points"] += 1
            classement[ext]["Points"] += 1

    df_classement = pd.DataFrame(classement).T
    df_classement["Différence"] = (
        df_classement["Buts Pour"] - df_classement["Buts Contre"]
    )
    df_classement.reset_index(inplace=True)
    df_classement.rename(columns={"index": "id"}, inplace=True)
    df_classement.index += 1

    # Ajout des noms des équipes
    df_classement["Equipe"] = df_classement["id"].apply(
        lambda id_: team.loc[
            team["team_api_id"] == id_, "team_long_name"
        ].values[0]
    )

    colonne_equipe = df_classement.pop("Equipe")
    df_classement.insert(0, "Equipe", colonne_equipe)

    # Tri final
    df_classement = df_classement.sort_values(
        by=["Points", "Différence", "Buts Pour"], ascending=False
    )

    return df_classement


# ---------------------- QUESTION 3 ----------------------


def choisir_match(saison, championnat):
    """
    Cette fonction sélectionne les matchs d'une saison donnée
    et d'un championnat spécifique.

    Args:
        saison (str) : Saison à analyser (ex : "2015/2016").
        championnat (str) : Nom du championnat (ex : "England Premier League").

    Retourne :
        DataFrame : Un DataFrame avec les colonnes 'home_team_api_id',
        'away_team_api_id', 'home_team_goal',
        et 'away_team_goal' pour les matchs filtrés.
    """
    df = pd.read_csv("data/Match_clean.csv", low_memory=False)
    leag = pd.read_csv("data/League.csv", low_memory=False)
    id = leag.loc[leag["name"] == championnat, "id"].values[0]

    df_filtre = df[(df["season"] == saison) & (df["league_id"] == id)]
    df_filtre = df_filtre[
        [
            "home_team_api_id",
            "away_team_api_id",
            "home_team_goal",
            "away_team_goal",
        ]
    ]

    return df_filtre


def taux_de_victoire(saison, championnat):
    """
    Cette fonction calcule le taux de victoire, nul et défaite à domicile et
    à l'extérieur pour une saison
    donnée et un championnat spécifique.

    Args:
        saison (str) : Saison à analyser (ex : "2015/2016").
        championnat (str) : Nom du championnat (ex : "England Premier League").

    Retourne :
        dict : Un dictionnaire avec les taux de victoire à domicile, nul et à
        l'extérieur sous forme de pourcentage.
    """
    matchs = choisir_match(saison, championnat)
    total = len(matchs)
    if total == 0:
        return {"Domicile": "0.0%", "Nul": "0.0%", "Exterieur": "0.0%"}

    dom, ext, nul = 0, 0, 0
    for _, match in matchs.iterrows():
        buts_dom, buts_ext = (
            match["home_team_goal"],
            match["away_team_goal"],
        )
        if buts_dom > buts_ext:
            dom += 1
        elif buts_dom < buts_ext:
            ext += 1
        else:
            nul += 1
    res = {
        "Domicile": dom / total,
        "Nul": nul / total,
        "Exterieur": ext / total,
    }
    res2 = {k: f"{v:.1%}" for k, v in res.items()}
    return res2


def question3():
    """
    Cette fonction permet à l'utilisateur de sélectionner un championnat
    via une fenêtre graphique, puis elle calcule le taux de victoire, nul
    et défaite à domicile et à l'extérieur pour la saison 2015/2016 du
    championnat sélectionné.

    Retourne :
        dict : Un dictionnaire avec les taux de victoire à domicile, nul et
        à l'extérieur sous forme de pourcentage.
    """

    # Import local : tkinter n'est nécessaire que pour cette fonction
    # interactive, ce qui évite une erreur sur les machines sans interface.
    import tkinter as tk
    from tkinter import ttk

    def fenetre_selection():
        """
        Cette fonction crée une fenêtre de sélection où l'utilisateur peut
        choisir un championnat parmi une liste prédéfinie.

        Retourne :
            str : Le nom du championnat sélectionné par l'utilisateur.
        """
        choix_utilisateur = {"valeur": None}

        def valider():
            """
            Cette fonction est appelée lorsque l'utilisateur valide son choix.
            Elle met à jour la valeur
            choisie par l'utilisateur et ferme la fenêtre.
            """
            choix_utilisateur["valeur"] = combo.get()
            fenetre_ui.destroy()

        fenetre_ui = tk.Tk()
        fenetre_ui.title("Choix du championnat")

        valeurs = [
            "Belgium Jupiler League",
            "England Premier League",
            "France Ligue 1",
            "Germany 1. Bundesliga",
            "Italy Serie A",
            "Netherlands Eredivisie",
            "Poland Ekstraklasa",
            "Portugal Liga ZON Sagres",
            "Scotland Premier League",
            "Spain LIGA BBVA",
            "Switzerland Super League",
        ]

        combo = ttk.Combobox(fenetre_ui, values=valeurs)
        combo.current(0)
        combo.pack(padx=10, pady=10)

        bouton = tk.Button(fenetre_ui, text="Valider", command=valider)
        bouton.pack(padx=10, pady=10)

        fenetre_ui.mainloop()
        return choix_utilisateur["valeur"]

    saison = "2015/2016"
    championnat = fenetre_selection()
    res = taux_de_victoire(saison, championnat)

    return res


def identifier_perdant(row):
    """
    Identifie l'équipe perdante d'un match.

    Paramètres :
    - row (pd.Series) : une ligne du DataFrame contenant les informations du match.

    Retourne :
    - int ou None : l'identifiant de l'équipe perdante, ou None en cas de match nul.
    """
    if row["home_team_goal"] < row["away_team_goal"]:
        return row["home_team_api_id"]
    elif row["home_team_goal"] > row["away_team_goal"]:
        return row["away_team_api_id"]
    else:
        return None


def equipe_avec_plus_defaites(
    match_file="data/Match_clean.csv", team_file="data/Team.csv"
):
    """
    Détermine l'équipe ayant enregistré le plus de défaites à partir de fichiers CSV.

    Paramètres :
    - match_file (str) : chemin vers le fichier CSV contenant les données de match.
    - team_file (str) : chemin vers le fichier CSV contenant les données des équipes.

    Retourne :
    - str : une phrase indiquant le nom de l'équipe avec le plus de défaites
    et le nombre de défaites.
    """
    df = pd.read_csv(match_file, low_memory=False)
    teams = pd.read_csv(team_file, low_memory=False)

    df["Perdant"] = df.apply(identifier_perdant, axis=1)
    df = df.dropna(subset=["Perdant"])

    defaites = df["Perdant"].value_counts()
    equipe_max_defaites_id = defaites.idxmax()
    nb_defaites = defaites.max()

    equipe_nom = teams.loc[
        teams["team_api_id"] == equipe_max_defaites_id, "team_long_name"
    ].values[0]

    return (
        f"L'équipe avec le plus de défaites est : {equipe_nom} "
        f"({nb_defaites} défaites)"
    )


def equipe_avec_plus_defaitess(
    match_file="data/Match_clean.csv", team_file="data/Team.csv"
):
    """
    Version alternative pour déterminer l'équipe ayant le plus de
    défaites, sans utiliser pandas.

    Paramètres :
    - match_file (str) : chemin vers le fichier CSV contenant les données de match.
    - team_file (str) : chemin vers le fichier CSV contenant les données des équipes.

    Retourne :
    - str : une phrase indiquant le nom de l'équipe avec le plus de
    défaites et le nombre de défaites.
    """
    with open(match_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        matches = list(reader)

    with open(team_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        teams = {
            row["team_api_id"]: row["team_long_name"] for row in reader
        }

    defaites = {}

    for row in matches:
        try:
            home_goals = int(row["home_team_goal"])
            away_goals = int(row["away_team_goal"])
            home_id = row["home_team_api_id"]
            away_id = row["away_team_api_id"]
        except ValueError:
            continue

        if home_goals < away_goals:
            perdant = home_id
        elif home_goals > away_goals:
            perdant = away_id
        else:
            continue

        if perdant not in defaites:
            defaites[perdant] = 1
        else:
            defaites[perdant] += 1

    equipe_max = max(defaites, key=defaites.get)
    nb_defaites = defaites[equipe_max]
    nom_equipe = teams.get(equipe_max, "Inconnu")

    return (f"L'équipe avec le plus de défaites est "
            f": {nom_equipe} ({nb_defaites} défaites)")


def afficher_boxplot_age_moyen(league_name, saison):
    """
    Affiche un boxplot représentant la distribution des âges moyens des équipes
    pour une ligue et une saison données.

    Paramètres :
    - league_name (str) : Nom de la ligue à analyser.
    - saison (str) : Saison au format "YYYY/YYYY" (ex. "2023/2024").
    """
    df_age = moyenne_age_equipes(league_name, saison)

    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df_age, y="Âge moyen", color="skyblue")
    plt.title(
        f"Distribution des âges moyens des équipes\n{league_name} - Saison {saison}"
    )
    plt.ylabel("Âge moyen des joueurs")
    plt.xlabel("")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("results/Questions/moyenne_age.png", dpi=300)


def moyenne_age_equipes(league_name, saison):
    """
    Calcule l'âge moyen des joueurs par équipe pour une ligue et une saison données.

    Paramètres :
        league_name (str) : Nom de la ligue (ex. "England Premier League").
        saison (str) : Saison au format "YYYY/YYYY" (ex. "2013/2014").

    Retourne :
        pd.DataFrame : Tableau contenant le nom des équipes et leur âge
        moyen, trié par âge décroissant.
    """
    matchs = pd.read_csv("data/Match_clean.csv", low_memory=False)
    players = pd.read_csv("data/Player.csv", low_memory=False)
    teams = pd.read_csv("data/Team.csv", low_memory=False)
    leagues = pd.read_csv("data/League.csv", low_memory=False)

    league_id = leagues[leagues["name"] == league_name]["id"].values[0]
    matchs_filtered = matchs[
        (matchs["league_id"] == league_id) & (matchs["season"] == saison)
    ]

    [f"home_player_{i}" for i in range(1, 12)] + [
        f"away_player_{i}" for i in range(1, 12)
    ]

    player_data = []
    for _, row in matchs_filtered.iterrows():
        match_date = pd.to_datetime(row["date"])
        for i in range(1, 12):
            player_id = row[f"home_player_{i}"]
            team_id = row["home_team_api_id"]
            if not pd.isna(player_id):
                player_data.append((team_id, player_id, match_date))
            player_id = row[f"away_player_{i}"]
            team_id = row["away_team_api_id"]
            if not pd.isna(player_id):
                player_data.append((team_id, player_id, match_date))

    player_df = pd.DataFrame(
        player_data, columns=["team_api_id", "player_api_id", "match_date"]
    )
    player_df = player_df.drop_duplicates(
        subset=["team_api_id", "player_api_id", "match_date"]
    )

    players["birthday"] = pd.to_datetime(players["birthday"])
    player_df = player_df.merge(
        players[["player_api_id", "birthday"]],
        on="player_api_id",
        how="left",
    )
    player_df["age"] = (
        player_df["match_date"] - player_df["birthday"]
    ).dt.days / 365.25

    avg_age_per_team = (
        player_df.groupby("team_api_id")["age"].mean().reset_index()
    )
    avg_age_per_team = avg_age_per_team.merge(
        teams[["team_api_id", "team_long_name"]],
        on="team_api_id",
        how="left",
    )
    avg_age_per_team = avg_age_per_team.rename(
        columns={"team_long_name": "Équipe", "age": "Âge moyen"}
    )
    avg_age_per_team = avg_age_per_team[
        ["Équipe", "Âge moyen"]
    ].sort_values(by="Âge moyen", ascending=False)

    return avg_age_per_team


def equipe_plus_clean_sheets(
    league_name="England Premier League", saison="2013/2014"
):
    """
    Identifie l'équipe ayant réalisé le plus de clean sheets (matchs
    sans encaisser de but) dans une ligue et une saison données.

    Paramètres :
        league_name (str) : Nom de la ligue (par défaut "England Premier League").
        saison (str) : Saison au format "YYYY/YYYY" (par défaut "2013/2014").

    Retourne :
        pd.DataFrame : Tableau des équipes et du nombre de clean
        sheets, trié par ordre décroissant.
    """
    matchs = pd.read_csv("data/Match_clean.csv", low_memory=False)
    leagues = pd.read_csv("data/League.csv", low_memory=False)
    teams = pd.read_csv("data/Team.csv", low_memory=False)

    league_data = leagues[leagues["name"] == league_name]
    if league_data.empty:
        print(f"Ligue '{league_name}' non trouvée.")
        return
    league_id = league_data["id"].values[0]

    matchs = matchs[
        (matchs["league_id"] == league_id) & (matchs["season"] == saison)
    ]
    if matchs.empty:
        print(
            f"Aucun match trouvé pour la ligue {league_name} et la saison {saison}."
        )
        return

    clean_sheets = {}
    for _, row in matchs.iterrows():
        try:
            if row["away_team_goal"] == 0:
                team_id = row["home_team_api_id"]
                clean_sheets[team_id] = clean_sheets.get(team_id, 0) + 1
            if row["home_team_goal"] == 0:
                team_id = row["away_team_api_id"]
                clean_sheets[team_id] = clean_sheets.get(team_id, 0) + 1
        except KeyError as e:
            print(f"Colonne manquante dans la ligne de match : {e}")

    if not clean_sheets:
        print("Aucune équipe n'a enregistré de clean sheets.")
        return

    clean_df = pd.DataFrame(
        list(clean_sheets.items()), columns=["team_api_id", "clean_sheets"]
    )
    clean_df = clean_df.merge(
        teams[["team_api_id", "team_long_name"]],
        on="team_api_id",
        how="left",
    )
    clean_df = clean_df.sort_values(by="clean_sheets", ascending=False)

    if clean_df.empty:
        print("Aucune équipe n'a de clean sheets.")
        return

    return clean_df
