"""Season window collection operations."""
from typing import Iterable, List
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import SeasonWindow
from . import cosmos_client


def save_season_windows(season_windows: Iterable[SeasonWindow]) -> None:
    normalized_season_windows = list(season_windows)
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    season_months = [season_window.season_month for season_window in normalized_season_windows]

    if not season_months:
        collection.delete_many({})
        return

    operations = [
        ReplaceOne(
            filter={"season_month": season_window.season_month},
            replacement=season_window.to_dict(),
            upsert=True,
        )
        for season_window in normalized_season_windows
    ]
    collection.bulk_write(operations, ordered=False)
    collection.delete_many({"season_month": {"$nin": season_months}})


def get_all_season_windows() -> List[SeasonWindow]:
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    docs = collection.find({})
    return sorted((SeasonWindow.from_dict(doc) for doc in docs), key=lambda season_window: season_window.season_month)
