import os
import unittest
from unittest import mock

os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING", "mongodb://localhost:27017")
os.environ.setdefault("POKER_APP_BASE_URL", "https://example.com/")

from offsuit_analyzer.datamodel import PlayerScore, Round
from offsuit_analyzer.web.services import admin_service


def _build_round() -> Round:
    return Round(
        round_id="1",
        bar_name="Test Bar",
        round_date="2026-09-25",
        bar_id="test-bar",
        players=(PlayerScore("player", 10),),
    )


class AdminServiceTests(unittest.TestCase):
    def test_refresh_rounds_database_logs_non_fatal_month_date_range_update_failures(self):
        rounds = [_build_round()]

        with mock.patch.object(
            admin_service.data_service,
            "get_this_months_rounds_for_bars",
            return_value=rounds,
        ) as mock_get_rounds, mock.patch.object(
            admin_service.persistence,
            "store_rounds",
        ) as mock_store_rounds, mock.patch.object(
            admin_service.month_date_range_service,
            "update_current_month_date_range",
            side_effect=ValueError("boom"),
        ) as mock_update_current_month_date_range, mock.patch.object(
            admin_service.logging_service,
            "log_warning",
        ) as mock_log_warning:
            admin_service.refresh_rounds_database()

        mock_get_rounds.assert_called_once_with()
        mock_store_rounds.assert_called_once_with(rounds)
        mock_update_current_month_date_range.assert_called_once_with(rounds)
        mock_log_warning.assert_called_once()
        self.assertIn("Failed to update month date range: boom", mock_log_warning.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
