import os
import unittest
from unittest.mock import patch

os.environ.setdefault("KEEP_THE_SCORE_BAR_TOKEN_WEEKNIGHT_PAIRS_JSON", "[]")
os.environ.setdefault("POKER_APP_BASE_URL", "")

from offsuit_analyzer.persistence import board_wipe_events_collection
from offsuit_analyzer.season_history import season_windows


class _FakeCollection:
    def __init__(self, docs=None):
        self.docs = list(docs or [])

    def find_one(self, filter_dict):
        for doc in self.docs:
            if all(doc.get(key) == value for key, value in filter_dict.items()):
                return dict(doc)
        return None

    def insert_one(self, doc):
        if any(existing.get("_id") == doc.get("_id") for existing in self.docs):
            raise AssertionError("duplicate marker insert in fake collection")
        self.docs.append(dict(doc))

    def find(self, filter_dict=None):
        if not filter_dict:
            return [dict(doc) for doc in self.docs]

        def matches(doc):
            for key, value in filter_dict.items():
                if isinstance(value, dict) and "$exists" in value:
                    if (key in doc) != value["$exists"]:
                        return False
                    continue
                if doc.get(key) != value:
                    return False
            return True

        return [dict(doc) for doc in self.docs if matches(doc)]

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

    def replace_one(self, filter_dict, replacement, upsert=False):
        for index, doc in enumerate(self.docs):
            if all(doc.get(key) == value for key, value in filter_dict.items()):
                self.docs[index] = dict(replacement)
                return
        if upsert:
            self.docs.append(dict(replacement))

    def delete_one(self, filter_dict):
        for index, doc in enumerate(self.docs):
            if all(doc.get(key) == value for key, value in filter_dict.items()):
                del self.docs[index]
                return


class _FakeDb(dict):
    def __getitem__(self, name):
        if name not in self:
            self[name] = _FakeCollection()
        return dict.__getitem__(self, name)


class AssignSeasonWindowsFromHistoryTests(unittest.TestCase):
    def test_assign_season_windows_from_history_migrates_legacy_event_date_records(self):
        fake_db = _FakeDb(
            {
                "boardWipeEventsCollectionProd": _FakeCollection(),
                "eventDatesCollectionProd": _FakeCollection(
                    [
                        {"event_date": "2024-01-06"},
                        {"event_date": "2024-01-13"},
                    ]
                ),
            }
        )

        with patch.object(board_wipe_events_collection.cosmos_client, "db", fake_db), \
             patch.object(board_wipe_events_collection.cosmos_client.config, "BOARD_WIPE_EVENTS_COLLECTION_NAME", "boardWipeEventsCollectionProd"), \
             patch.object(board_wipe_events_collection.cosmos_client.config, "IS_DEVELOPMENT_ENV", False), \
             patch.object(season_windows.persistence, "get_all_board_wipe_events", side_effect=board_wipe_events_collection.get_all_board_wipe_events), \
             patch.object(season_windows.persistence, "save_season_windows") as save_mock:
            result = season_windows.assign_season_windows_from_history()

        self.assertEqual(1, len(result))
        self.assertEqual("2024-01-06", result[0].start_date.isoformat())
        self.assertEqual("2024-01-19", result[0].end_date.isoformat())
        save_mock.assert_called_once_with(result)
        migrated_docs = fake_db["boardWipeEventsCollectionProd"].find({"board_wipe_date": {"$exists": True}})
        self.assertEqual(
            ["2024-01-06", "2024-01-13"],
            sorted(doc["board_wipe_date"] for doc in migrated_docs),
        )


if __name__ == "__main__":
    unittest.main()
