import os
import unittest
from unittest.mock import MagicMock, patch


os.environ.setdefault("POKER_APP_BASE_URL", "http://example/")
os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING", "mongodb://localhost:27017")

from offsuit_analyzer.datamodel import EventDate, PlayerScore, Round
from offsuit_analyzer.persistence import event_dates_collection
from offsuit_analyzer.web.services import admin_service, season_assignment_service


class FakeCollection:
    def __init__(self):
        self.docs = {}

    def bulk_write(self, operations, ordered=False):
        for operation in operations:
            key = tuple(sorted(operation._filter.items()))
            self.docs[key] = dict(operation._doc)

    def find(self, query):
        return list(self.docs.values())


class SeasonHistoryTests(unittest.TestCase):
    def test_record_event_dates_persists_distinct_dates(self):
        fake_collection = FakeCollection()
        fake_db = {event_dates_collection.cosmos_client.config.EVENT_DATES_COLLECTION_NAME: fake_collection}

        with patch.object(event_dates_collection.cosmos_client, "db", fake_db):
            event_dates_collection.record_event_dates(["2026-09-05", "2026-09-05", "2026-09-12"])
            stored_event_dates = event_dates_collection.get_all_event_dates()

        self.assertEqual(
            [event_date.event_date.isoformat() for event_date in stored_event_dates],
            ["2026-09-05", "2026-09-12"],
        )

    def test_assign_season_windows_rebuilds_multiple_historical_seasons(self):
        historical_event_dates = [
            "2026-08-06",
            "2026-08-13",
            "2026-08-20",
            "2026-08-27",
            "2026-09-03",
            "2026-09-10",
            "2026-09-17",
            "2026-09-24",
            "2026-10-01",
            "2026-10-08",
            "2026-10-15",
            "2026-10-22",
            "2026-10-29",
        ]
        fake_event_dates_collection = MagicMock()
        fake_event_dates_collection.get_all_event_dates.return_value = [
            EventDate(event_date=event_date) for event_date in historical_event_dates
        ]
        fake_season_windows_collection = MagicMock()

        with patch.object(season_assignment_service, "event_dates_collection", fake_event_dates_collection), patch.object(
            season_assignment_service,
            "season_windows_collection",
            fake_season_windows_collection,
        ):
            season_windows = season_assignment_service.assign_season_windows_from_history()

        self.assertEqual(
            [
                (
                    season_window.season_month,
                    season_window.start_date.isoformat(),
                    season_window.end_date.isoformat(),
                )
                for season_window in season_windows
            ],
            [
                (202608, "2026-08-01", "2026-08-28"),
                (202609, "2026-08-29", "2026-10-02"),
                (202610, "2026-10-03", "2026-10-30"),
            ],
        )
        fake_season_windows_collection.save_season_windows.assert_called_once_with(season_windows)

    def test_refresh_rounds_records_observed_event_dates(self):
        rounds = [
            Round(
                round_id="1",
                bar_name="Bar One",
                round_date="2026-09-05",
                bar_id="bar-1",
                players=(PlayerScore(player_name="alice", points=10),),
            ),
            Round(
                round_id="2",
                bar_name="Bar Two",
                round_date="2026-09-05",
                bar_id="bar-2",
                players=(PlayerScore(player_name="bob", points=15),),
            ),
            Round(
                round_id="3",
                bar_name="Bar Three",
                round_date="2026-09-12",
                bar_id="bar-3",
                players=(PlayerScore(player_name="carol", points=20),),
            ),
        ]

        with patch.object(admin_service.data_service, "get_this_months_rounds_for_bars", return_value=rounds), patch.object(
            admin_service.persistence,
            "store_rounds",
        ) as store_rounds, patch.object(admin_service.persistence, "record_event_dates") as record_event_dates:
            admin_service.refresh_rounds_database()

        store_rounds.assert_called_once_with(rounds)
        record_event_dates.assert_called_once_with(["2026-09-05", "2026-09-12"])

    def test_assign_season_windows_handles_empty_history(self):
        self.assertEqual(season_assignment_service.calculate_season_windows([]), [])


if __name__ == "__main__":
    unittest.main()
