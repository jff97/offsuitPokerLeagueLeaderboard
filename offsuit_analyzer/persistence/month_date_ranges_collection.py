"""Month date range collection operations."""
from typing import Optional
from pymongo import ReplaceOne
from offsuit_analyzer.datamodel.month_date_range import MonthDateRange
from . import cosmos_client


def save_month_date_range(month_date_range: MonthDateRange) -> None:
    """Upsert a single month date range keyed by YYYYMM."""
    collection = cosmos_client.db[cosmos_client.config.MONTH_DATE_RANGES_COLLECTION_NAME]
    operation = ReplaceOne(
        filter={"month_key": month_date_range.month_key},
        replacement=month_date_range.to_dict(),
        upsert=True
    )
    collection.bulk_write([operation], ordered=False)


def get_month_date_range(month_key: int) -> Optional[MonthDateRange]:
    """Read a stored month date range by its YYYYMM key."""
    collection = cosmos_client.db[cosmos_client.config.MONTH_DATE_RANGES_COLLECTION_NAME]
    doc = collection.find_one({"month_key": month_key})

    if doc is None:
        return None

    return MonthDateRange.from_dict(doc)
