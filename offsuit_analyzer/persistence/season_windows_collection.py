"""Season window collection operations."""
from typing import List
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import SeasonWindow
from . import cosmos_client


def save_season_windows(season_windows: List[SeasonWindow]) -> None:
    """Save the given season windows, removing any not in the list."""
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    if not season_windows:
        collection.delete_many({})
        return

    operations = [
        ReplaceOne(
            filter={"year": season_window.year, "month": season_window.month},
            replacement=season_window.to_dict(),
            upsert=True,
        )
        for season_window in season_windows
    ]
    collection.bulk_write(operations, ordered=False)

    valid_year_month_filters = [{"year": season_window.year, "month": season_window.month} for season_window in season_windows]
    collection.delete_many({"$nor": valid_year_month_filters})


def get_all_season_windows() -> List[SeasonWindow]:
    collection = cosmos_client.db[cosmos_client.config.SEASON_WINDOWS_COLLECTION_NAME]
    docs = collection.find({"year": {"$exists": True}, "month": {"$exists": True}})
    return sorted(
        (SeasonWindow.from_dict(doc) for doc in docs),
        key=lambda season_window: (season_window.year, season_window.month),
    )
