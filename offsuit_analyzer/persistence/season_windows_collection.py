"""Season window collection operations."""
from typing import Iterable, List
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import SeasonWindow
from . import cosmos_client


def save_season_windows(season_windows: Iterable[SeasonWindow]) -> None:
    normalized_season_windows = list(season_windows)
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    valid_year_month_pairs = {(season_window.year, season_window.month) for season_window in normalized_season_windows}

    if not valid_year_month_pairs:
        collection.delete_many({})
        return

    operations = [
        ReplaceOne(
            filter={"year": season_window.year, "month": season_window.month},
            replacement=season_window.to_dict(),
            upsert=True,
        )
        for season_window in normalized_season_windows
    ]
    collection.bulk_write(operations, ordered=False)

    stale_ids = [
        doc["_id"]
        for doc in collection.find({}, {"_id": 1, "year": 1, "month": 1})
        if (doc.get("year"), doc.get("month")) not in valid_year_month_pairs
    ]
    if stale_ids:
        collection.delete_many({"_id": {"$in": stale_ids}})


def get_all_season_windows() -> List[SeasonWindow]:
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    docs = collection.find({})
    return sorted(
        (SeasonWindow.from_dict(doc) for doc in docs),
        key=lambda season_window: (season_window.year, season_window.month),
    )
