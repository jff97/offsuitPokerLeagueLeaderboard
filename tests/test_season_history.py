import os
import unittest
from unittest.mock import MagicMock, patch


os.environ.setdefault("POKER_APP_BASE_URL", "http://example/")
os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("OFFSUIT_ANALYZER_COSMOS_DB_CONNECTION_STRING", "mongodb://localhost:27017")

from offsuit_analyzer.datamodel import EventDate, PlayerScore, Round, SeasonWindow
from offsuit_analyzer.persistence import event_dates_collection, season_windows_collection
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

    def delete_many(self, query):
        if not query:
            self.docs = {}
            return

        season_month_filter = query.get("season_month", {})
        allowed_season_months = set(season_month_filter.get("$nin", []))
        if allowed_season_months:
            self.docs = {
                key: value
                for key, value in self.docs.items()
                if value.get("season_month") in allowed_season_months
            }


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

    def test_refresh_rounds_seeds_event_dates_from_all_stored_rounds_when_empty(self):
        current_rounds = [
            Round(
                round_id="2",
                bar_name="Bar One",
                round_date="2026-09-05",
                bar_id="bar-1",
                players=(PlayerScore(player_name="alice", points=10),),
            ),
            Round(
                round_id="3",
                bar_name="Bar Two",
                round_date="2026-09-05",
                bar_id="bar-2",
                players=(PlayerScore(player_name="bob", points=15),),
            ),
            Round(
                round_id="4",
                bar_name="Bar Four",
                round_date="2026-09-19",
                bar_id="bar-4",
                players=(PlayerScore(player_name="dave", points=30),),
            ),
        ]
        all_stored_rounds = [
            Round(
                round_id="1",
                bar_name="Historic Bar",
                round_date="2026-08-29",
                bar_id="bar-0",
                players=(PlayerScore(player_name="zed", points=25),),
            ),
            *current_rounds,
            Round(
                round_id="5",
                bar_name="Bar Three",
                round_date="2026-09-12",
                bar_id="bar-3",
                players=(PlayerScore(player_name="carol", points=20),),
            ),
        ]

        with patch.object(admin_service.data_service, "get_this_months_rounds_for_bars", return_value=current_rounds), patch.object(
            admin_service.persistence,
            "store_rounds",
        ) as store_rounds, patch.object(admin_service.persistence, "get_all_event_dates", return_value=[]), patch.object(
            admin_service.persistence,
            "get_all_round_dates",
            return_value=admin_service._get_observed_event_dates(all_stored_rounds),
        ), patch.object(
            admin_service.persistence,
            "record_event_dates",
        ) as record_event_dates:
            admin_service.refresh_rounds_database()

        store_rounds.assert_called_once_with(current_rounds)
        record_event_dates.assert_called_once_with(["2026-08-29", "2026-09-05", "2026-09-12", "2026-09-19"])

    def test_refresh_rounds_records_current_round_event_dates_when_history_exists(self):
        current_rounds = [
            Round(
                round_id="2",
                bar_name="Bar One",
                round_date="2026-09-05",
                bar_id="bar-1",
                players=(PlayerScore(player_name="alice", points=10),),
            ),
            Round(
                round_id="3",
                bar_name="Bar Two",
                round_date="2026-09-12",
                bar_id="bar-2",
                players=(PlayerScore(player_name="bob", points=15),),
            ),
        ]

        with patch.object(admin_service.data_service, "get_this_months_rounds_for_bars", return_value=current_rounds), patch.object(
            admin_service.persistence,
            "store_rounds",
        ) as store_rounds, patch.object(
            admin_service.persistence,
            "get_all_event_dates",
            return_value=[
                EventDate(event_date="2026-08-29"),
                EventDate(event_date="2026-09-05"),
                EventDate(event_date="2026-09-12"),
            ],
        ), patch.object(
            admin_service.persistence,
            "get_all_round_dates",
            return_value=["2026-08-29", "2026-09-05", "2026-09-12"],
        ), patch.object(
            admin_service.persistence,
            "record_event_dates",
        ) as record_event_dates:
            admin_service.refresh_rounds_database()

        store_rounds.assert_called_once_with(current_rounds)
        record_event_dates.assert_called_once_with(["2026-09-05", "2026-09-12"])

    def test_refresh_rounds_backfills_missing_stored_round_dates_when_history_incomplete(self):
        current_rounds = [
            Round(
                round_id="2",
                bar_name="Bar One",
                round_date="2026-09-05",
                bar_id="bar-1",
                players=(PlayerScore(player_name="alice", points=10),),
            ),
        ]

        with patch.object(admin_service.data_service, "get_this_months_rounds_for_bars", return_value=current_rounds), patch.object(
            admin_service.persistence,
            "store_rounds",
        ), patch.object(
            admin_service.persistence,
            "get_all_event_dates",
            return_value=[EventDate(event_date="2026-09-05")],
        ), patch.object(
            admin_service.persistence,
            "get_all_round_dates",
            return_value=["2026-08-29", "2026-09-05"],
        ), patch.object(
            admin_service.persistence,
            "record_event_dates",
        ) as record_event_dates:
            admin_service.refresh_rounds_database()

        record_event_dates.assert_called_once_with(["2026-08-29", "2026-09-05"])

    def test_assign_season_windows_handles_empty_history(self):
        self.assertEqual(season_assignment_service.calculate_season_windows([]), [])

    def test_assign_season_windows_from_history_clears_with_empty_history(self):
        fake_event_dates_collection = MagicMock()
        fake_event_dates_collection.get_all_event_dates.return_value = []
        fake_season_windows_collection = MagicMock()

        with patch.object(season_assignment_service, "event_dates_collection", fake_event_dates_collection), patch.object(
            season_assignment_service,
            "season_windows_collection",
            fake_season_windows_collection,
        ):
            season_windows = season_assignment_service.assign_season_windows_from_history()

        self.assertEqual(season_windows, [])
        fake_season_windows_collection.save_season_windows.assert_called_once_with([])

    def test_save_season_windows_replaces_stale_months(self):
        fake_collection = FakeCollection()
        fake_db = {season_windows_collection.cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME: fake_collection}

        with patch.object(season_windows_collection.cosmos_client, "db", fake_db):
            season_windows_collection.save_season_windows(
                [
                    SeasonWindow(season_month=202608, start_date="2026-08-01", end_date="2026-08-28"),
                    SeasonWindow(season_month=202609, start_date="2026-08-29", end_date="2026-10-02"),
                ]
            )
            season_windows_collection.save_season_windows(
                [
                    SeasonWindow(season_month=202609, start_date="2026-08-29", end_date="2026-10-02"),
                ]
            )
            stored_season_windows = season_windows_collection.get_all_season_windows()

        self.assertEqual(
            [(season_window.season_month, season_window.start_date.isoformat(), season_window.end_date.isoformat()) for season_window in stored_season_windows],
            [(202609, "2026-08-29", "2026-10-02")],
        )


if __name__ == "__main__":
    unittest.main()
