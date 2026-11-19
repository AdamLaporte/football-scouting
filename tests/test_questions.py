import tempfile
import unittest
import pandas as pd
from io import StringIO
import sys
import os

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
)
from questions import (  # noqa: E402
    process_largest_goal_difference,
    analyze_league_matches,
    charger_donnees_matchs,
    trouver_plus_grosse_cote,
)


class TestFootballFunctions(unittest.TestCase):

    def setUp(self):
        # Les fonctions écrivent dans results/Questions : on travaille
        # dans un dossier temporaire pour ne rien polluer.
        self._cwd = os.getcwd()
        self._tmp = tempfile.TemporaryDirectory()
        os.chdir(self._tmp.name)
        os.makedirs("results/Questions")

        self.match_data = StringIO(
            """
id,league_id,date,season,home_team_api_id,away_team_api_id,home_team_goal,away_team_goal,B365H,B365D,B365A
1,1,2023-08-01,2023/2024,10,20,2,1,1.8,3.5,4.2
2,1,2023-08-02,2023/2024,15,25,3,2,1.9,3.4,4.0
3,1,2023-08-03,2023/2024,10,25,4,4,2.1,3.2,3.8
4,1,2023-08-04,2023/2024,20,15,1,3,2.0,3.1,4.5
"""
        )

        self.team_data = StringIO(
            """
team_api_id,team_long_name
10,Team A
20,Team B
15,Team C
25,Team D
"""
        )

        self.league_data = StringIO(
            """
id,name
1,League A
"""
        )

    def tearDown(self):
        os.chdir(self._cwd)
        self._tmp.cleanup()

    def test_process_largest_goal_difference(self):
        self.match_data.seek(0)
        self.team_data.seek(0)
        self.league_data.seek(0)
        result = process_largest_goal_difference(
            self.match_data, self.team_data, self.league_data, "output.csv"
        )
        self.assertEqual(result.shape[0], 1)
        self.assertTrue("league_name" in result.columns)
        self.assertTrue("home_team_name" in result.columns)

    def test_analyze_league_matches(self):
        self.match_data.seek(0)
        self.team_data.seek(0)
        result = analyze_league_matches(
            1, self.match_data, self.team_data, "output.csv"
        )
        self.assertEqual(result.shape[0], 1)
        self.assertEqual(
            result.columns.tolist(),
            ["season", "team_long_name", "win_count"],
        )

    def test_charger_donnees_matchs(self):
        self.match_data.seek(0)
        self.team_data.seek(0)
        result = charger_donnees_matchs(self.match_data, self.team_data)
        self.assertTrue("home_team_name" in result.columns)
        self.assertTrue("away_team_name" in result.columns)
        self.assertEqual(result.shape[0], 4)

    def test_trouver_plus_grosse_cote(self):
        self.match_data.seek(0)
        matchs_df = pd.read_csv(self.match_data)

        result_home = trouver_plus_grosse_cote(matchs_df, "home")
        self.assertEqual(result_home["B365H"].values[0], 1.9)

        result_away = trouver_plus_grosse_cote(matchs_df, "away")
        if not result_away.empty:
            self.assertEqual(result_away["B365A"].values[0], 4.5)
        else:
            self.fail("Aucun match à l'extérieur trouvé pour le test.")

        result_draw = trouver_plus_grosse_cote(matchs_df, "draw")
        if not result_draw.empty:
            self.assertEqual(result_draw["B365D"].values[0], 3.2)
        else:
            self.fail("Aucun match nul trouvé pour le test.")

    def test_invalid_choice_trouver_plus_grosse_cote(self):
        self.match_data.seek(0)
        matchs_df = pd.read_csv(self.match_data)
        with self.assertRaises(ValueError):
            trouver_plus_grosse_cote(matchs_df, "invalid_choice")


if __name__ == "__main__":
    unittest.main()
