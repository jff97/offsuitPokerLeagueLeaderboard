import os
import unittest
from unittest.mock import patch

os.environ.setdefault("POKER_APP_BASE_URL", "https://example.com/")
os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING", "mongodb://localhost:27017")

from offsuit_analyzer.datamodel.player_score import PlayerScore
from offsuit_analyzer.datamodel.round import Round
from offsuit_analyzer.web.app import app
from offsuit_analyzer.web.services import wheel_qualifiers_service


def make_round(round_id, bar_name, players):
    return Round(
        round_id=round_id,
        bar_name=bar_name,
        round_date="2026-09-01",
        bar_id=f"{bar_name}-id",
        players=tuple(
            PlayerScore(player_name=player_name, points=points)
            for player_name, points in players
        ),
    )


class WheelQualifierServiceTests(unittest.TestCase):
    def test_get_players_who_played_every_round_by_bar(self):
        rounds = [
            make_round("1", "Bar A", [("alice", 10), ("bob", 9), ("carol", 8)]),
            make_round("2", "Bar A", [("alice", 7), ("bob", 6), ("dave", 5)]),
            make_round("3", "Bar B", [("erin", 10), ("frank", 9)]),
            make_round("4", "Bar B", [("erin", 4), ("frank", 3), ("gina", 2)]),
        ]

        result = wheel_qualifiers_service.get_players_who_played_every_round_by_bar(rounds)

        self.assertEqual(result, {"Bar A": ["alice", "bob"], "Bar B": ["erin", "frank"]})

    @patch(
        "offsuit_analyzer.web.services.wheel_qualifiers_service.excluded_qualifiers_collection.get_excluded_players",
        return_value={"dave"},
    )
    @patch(
        "offsuit_analyzer.web.services.wheel_qualifiers_service.data_service.get_this_months_rounds_for_bars"
    )
    def test_get_wheel_qualifiers_filters_qualified_and_unavailable(
        self, mock_get_rounds, _
    ):
        mock_get_rounds.return_value = [
            make_round(
                "1",
                "Bar A",
                [("alice", 30), ("bob", 25), ("carol", 20), ("dave", 15), ("erin", 10)],
            ),
            make_round(
                "2",
                "Bar A",
                [("alice", 10), ("bob", 9), ("carol", 8), ("dave", 7), ("erin", 6)],
            ),
        ]

        result = wheel_qualifiers_service.get_wheel_qualifiers_by_bar()

        self.assertEqual(result, {"Bar A": ["erin"]})

    def test_admin_endpoint_exposes_wheel_qualifiers_without_auth(self):
        with patch(
            "offsuit_analyzer.web.controllers.admin_controller.wheel_qualifiers_service.get_wheel_qualifiers_by_bar",
            return_value={"Bar A": ["erin"]},
        ):
            with app.test_client() as client:
                response = client.get("/api/admin/wheelqualifiers")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"Bar A": ["erin"]})


if __name__ == "__main__":
    unittest.main()
