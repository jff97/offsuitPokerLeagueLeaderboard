import os
import unittest

os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING", "mongodb://localhost:27017")
os.environ.setdefault("POKER_APP_BASE_URL", "https://example.com/")

from offsuit_analyzer.datamodel import PlayerScore, Round
from offsuit_analyzer.web.services import month_date_range_service


def _build_round(round_id: str, round_date: str) -> Round:
    return Round(
        round_id=round_id,
        bar_name="Test Bar",
        round_date=round_date,
        bar_id="test-bar",
        players=(PlayerScore("player", 10),),
    )


class MonthDateRangeServiceTests(unittest.TestCase):
    def test_build_current_month_date_range_uses_same_month_key_for_same_month_bounds(self):
        rounds = [
            _build_round("1", "2026-10-03"),
            _build_round("2", "2026-10-20"),
        ]

        month_date_range = month_date_range_service.build_current_month_date_range(rounds)

        self.assertIsNotNone(month_date_range)
        self.assertEqual(202610, month_date_range.month_key)
        self.assertEqual("2026-10-03", month_date_range.start_date)
        self.assertEqual("2026-10-20", month_date_range.end_date)

    def test_build_current_month_date_range_uses_midpoint_month_key_across_months(self):
        rounds = [
            _build_round("1", "2026-08-29"),
            _build_round("2", "2026-09-25"),
        ]

        month_date_range = month_date_range_service.build_current_month_date_range(rounds)

        self.assertIsNotNone(month_date_range)
        self.assertEqual(202609, month_date_range.month_key)
        self.assertEqual("2026-08-29", month_date_range.start_date)
        self.assertEqual("2026-09-25", month_date_range.end_date)

    def test_merge_month_date_ranges_raises_for_mismatched_keys(self):
        existing_month_date_range = month_date_range_service.MonthDateRange(
            month_key=202608,
            start_date="2026-08-01",
            end_date="2026-08-31",
        )
        observed_month_date_range = month_date_range_service.MonthDateRange(
            month_key=202609,
            start_date="2026-08-29",
            end_date="2026-09-25",
        )

        with self.assertRaises(ValueError):
            month_date_range_service.merge_month_date_ranges(
                existing_month_date_range,
                observed_month_date_range,
            )


if __name__ == "__main__":
    unittest.main()
