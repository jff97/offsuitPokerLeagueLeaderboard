import os
from datetime import date
import unittest
from unittest.mock import patch

os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("POKER_APP_BASE_URL", "")

from offsuit_analyzer.datamodel import BoardWipeEvent, Round, SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_year_month
from offsuit_analyzer.season_history import board_wipe_events, season_windows


class BoardWipeEventsTests(unittest.TestCase):
    def test_get_board_wipe_dates_to_record_merges_in_stored_round_dates(self):
        rounds = [
            Round("1", "A", "2024-01-06", "bar-1", ()),
            Round("2", "A", "2024-01-13", "bar-1", ()),
        ]

        with patch.object(board_wipe_events.persistence, "get_all_board_wipe_events", return_value=[BoardWipeEvent("2024-01-06")]), \
             patch.object(board_wipe_events.persistence, "get_all_round_dates", return_value=["2023-12-30"]):
            self.assertEqual(
                ["2023-12-30", "2024-01-06", "2024-01-13"],
                board_wipe_events.get_board_wipe_dates_to_record(rounds),
            )


class SeasonWindowsTests(unittest.TestCase):
    def test_derive_year_month_uses_midpoint(self):
        self.assertEqual((2024, 1), derive_year_month("2023-12-30", "2024-01-05"))

    def test_calculate_season_windows_groups_by_boundary_week_and_year_month(self):
        result = season_windows.calculate_season_windows(
            ["2024-01-06", "2024-01-13", "2024-02-03"],
        )

        self.assertEqual(
            [
                SeasonWindow(year=2024, month=1, start_date=date(2024, 1, 6), end_date=date(2024, 1, 19)),
                SeasonWindow(year=2024, month=2, start_date=date(2024, 2, 3), end_date=date(2024, 2, 9)),
            ],
            result,
        )

    def test_assign_season_windows_from_history_reads_board_wipe_events(self):
        stored_events = [BoardWipeEvent("2024-01-06"), BoardWipeEvent("2024-01-13")]

        with patch.object(season_windows.persistence, "get_all_board_wipe_events", return_value=stored_events), \
             patch.object(season_windows.persistence, "save_season_windows") as save_mock:
            result = season_windows.assign_season_windows_from_history()

        self.assertEqual(1, len(result))
        self.assertEqual(2024, result[0].year)
        self.assertEqual(1, result[0].month)
        self.assertEqual("2024-01-06", result[0].start_date.isoformat())
        self.assertEqual("2024-01-19", result[0].end_date.isoformat())
        save_mock.assert_called_once_with(result)


if __name__ == "__main__":
    unittest.main()
