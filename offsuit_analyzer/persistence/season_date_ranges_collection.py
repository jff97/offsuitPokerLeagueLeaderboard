"""Season date range collection operations."""
from typing import Optional
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


def get_season_date_range(season_month: int) -> Optional[SeasonDateRange]:
    """Read the stored season date range for a single YYYYMM key."""
    collection = cosmos_client.db[cosmos_client.config.SEASON_DATE_RANGES_COLLECTION_NAME]
    doc = collection.find_one({"season_month": season_month})

    if doc is None:
        return None

    return SeasonDateRange.from_dict(doc)
