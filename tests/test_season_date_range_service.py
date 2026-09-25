import unittest
from datetime import date
import sys
import types
from unittest.mock import patch

from offsuit_analyzer.datamodel import Round, SeasonDateRange

fake_season_date_ranges_collection = types.ModuleType("season_date_ranges_collection")
fake_season_date_ranges_collection.get_season_date_range = lambda season_month: None
fake_season_date_ranges_collection.save_season_date_range = lambda season_date_range: None

fake_persistence = types.ModuleType("offsuit_analyzer.persistence")
fake_persistence.season_date_ranges_collection = fake_season_date_ranges_collection

sys.modules.setdefault("offsuit_analyzer.persistence", fake_persistence)
sys.modules.setdefault(
    "offsuit_analyzer.persistence.season_date_ranges_collection",
    fake_season_date_ranges_collection,
)

from offsuit_analyzer.web.services import season_date_range_service


class SeasonDateRangeServiceTests(unittest.TestCase):
    def test_empty_rounds_create_seeded_current_month_record_when_missing(self):
        current_poker_date = date(2026, 10, 1)
        expected_range = SeasonDateRange(
            start_date=current_poker_date,
            end_date=current_poker_date,
        )

        with patch.object(
                 season_date_range_service,
                 "_get_current_poker_date",
                 return_value=current_poker_date,
             ), patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "get_season_date_range",
                 return_value=None,
             ) as get_season_date_range, \
             patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "save_season_date_range",
             ) as save_season_date_range:
            result = season_date_range_service.update_current_season_date_range([])

        self.assertTrue(result)
        get_season_date_range.assert_called_once_with(expected_range.season_month)
        save_season_date_range.assert_called_once_with(expected_range)

    def test_empty_rounds_preserve_existing_current_month_record(self):
        existing_range = SeasonDateRange(
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15),
        )
        current_poker_date = date(2026, 10, 1)

        with patch.object(
                 season_date_range_service,
                 "_get_current_poker_date",
                 return_value=current_poker_date,
             ), patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "get_season_date_range",
                 return_value=existing_range,
             ) as get_season_date_range, \
             patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "save_season_date_range",
             ) as save_season_date_range:
            result = season_date_range_service.update_current_season_date_range([])

        self.assertTrue(result)
        get_season_date_range.assert_called_once_with(existing_range.season_month)
        save_season_date_range.assert_not_called()

    def test_near_empty_previous_month_rounds_seed_current_month_record(self):
        stale_round = self._round("stale-round", "2026-09-30")
        current_poker_date = date(2026, 10, 1)
        expected_range = SeasonDateRange(
            start_date=current_poker_date,
            end_date=current_poker_date,
        )

        with patch.object(
                 season_date_range_service,
                 "_get_current_poker_date",
                 return_value=current_poker_date,
             ), patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "get_season_date_range",
                 return_value=None,
             ) as get_season_date_range, \
             patch.object(
                 season_date_range_service.season_date_ranges_collection,
                 "save_season_date_range",
             ) as save_season_date_range:
            result = season_date_range_service.update_current_season_date_range([stale_round])

        self.assertTrue(result)
        get_season_date_range.assert_called_once_with(expected_range.season_month)
        save_season_date_range.assert_called_once_with(expected_range)

    def test_dated_rounds_continue_to_merge_existing_season_range(self):
        existing_range = SeasonDateRange(
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 12),
        )
        rounds = [
            self._round("round-1", "2026-09-05"),
            self._round("round-2", "2026-09-19"),
        ]

        with patch.object(
            season_date_range_service.season_date_ranges_collection,
            "get_season_date_range",
            return_value=existing_range,
        ) as get_season_date_range, patch.object(
            season_date_range_service.season_date_ranges_collection,
            "save_season_date_range",
        ) as save_season_date_range:
            result = season_date_range_service.update_current_season_date_range(rounds)

        self.assertTrue(result)
        get_season_date_range.assert_called_once_with(existing_range.season_month)
        save_season_date_range.assert_called_once_with(
            SeasonDateRange(
                start_date=date(2026, 9, 1),
                end_date=date(2026, 9, 19),
            )
        )

    @staticmethod
    def _round(round_id: str, round_date: str) -> Round:
        return Round(
            round_id=round_id,
            bar_name="Test Bar",
            round_date=round_date,
            bar_id="bar-1",
            players=(),
        )


if __name__ == "__main__":
    unittest.main()
