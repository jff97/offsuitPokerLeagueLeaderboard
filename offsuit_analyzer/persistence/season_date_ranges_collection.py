"""Season date range collection operations."""
from typing import List
from pymongo import ReplaceOne
from offsuit_analyzer.datamodel.season_date_range import SeasonDateRange
from . import cosmos_client


def save_season_date_range(season_date_range: SeasonDateRange) -> None:
    """Upsert a single season date range keyed by YYYYMM."""
    collection = cosmos_client.db[cosmos_client.config.SEASON_DATE_RANGES_COLLECTION_NAME]
    operation = ReplaceOne(
        filter={"season_month": season_date_range.season_month},
        replacement=season_date_range.to_dict(),
        upsert=True
    )
    collection.bulk_write([operation], ordered=False)


def get_season_date_ranges(season_month: int) -> List[SeasonDateRange]:
    """Read all stored season date ranges for a single YYYYMM key."""
    collection = cosmos_client.db[cosmos_client.config.SEASON_DATE_RANGES_COLLECTION_NAME]
    docs = list(collection.find({"season_month": season_month}))
    return [SeasonDateRange.from_dict(doc) for doc in docs]
