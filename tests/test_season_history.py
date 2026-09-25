import os
from datetime import date
import unittest
from unittest.mock import patch

os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("POKER_APP_BASE_URL", "")

from offsuit_analyzer.datamodel import BoardWipeEvent, Round, SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_year_month
from offsuit_analyzer.persistence import board_wipe_events_collection
from offsuit_analyzer.season_history import board_wipe_events, season_windows


class _FakeBoardWipeCollection:
    def __init__(self, docs=None):
        self.docs = list(docs or [])

    def bulk_write(self, operations, ordered=False):
        for operation in operations:
            target_value = operation._filter["board_wipe_date"]
            replacement = dict(operation._doc)
            for index, doc in enumerate(self.docs):
                if doc.get("board_wipe_date") == target_value:
                    self.docs[index] = replacement
                    break
            else:
                self.docs.append(replacement)

    def delete_many(self, filter_dict):
        if not filter_dict:
            self.docs = []
            return

        excluded_dates = set(filter_dict["board_wipe_date"]["$nin"])
        self.docs = [doc for doc in self.docs if doc.get("board_wipe_date") in excluded_dates]

    def find(self, filter_dict=None):
        return list(self.docs)


class _FakeDb(dict):
    def __getitem__(self, name):
        return dict.__getitem__(self, name)


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

    def test_record_board_wipe_events_replaces_stale_dates(self):
        collection = _FakeBoardWipeCollection(
            [
                {"board_wipe_date": "2023-12-30"},
                {"board_wipe_date": "2024-01-06"},
            ]
        )
        fake_db = _FakeDb({"boardWipeEventsCollectionProd": collection})

        with patch.object(board_wipe_events_collection.cosmos_client, "db", fake_db), \
             patch.object(
                 board_wipe_events_collection.cosmos_client.config,
                 "BOARD_WIPE_EVENTS_COLLECTION_NAME",
                 "boardWipeEventsCollectionProd",
             ):
            board_wipe_events_collection.record_board_wipe_events(["2024-01-06", "2024-01-13"])

        self.assertEqual(
            ["2024-01-06", "2024-01-13"],
            [doc["board_wipe_date"] for doc in collection.find({})],
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
