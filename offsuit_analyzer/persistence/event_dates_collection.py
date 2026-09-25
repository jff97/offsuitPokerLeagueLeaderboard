"""Event date collection operations."""
from typing import Iterable, List, Union
from datetime import date
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import EventDate
from . import cosmos_client


def record_event_dates(event_dates: Iterable[Union[str, date]]) -> None:
    """Persist distinct observed event dates keyed by the raw day."""
    normalized_event_dates = sorted({EventDate(event_date=event_date) for event_date in event_dates}, key=_sort_key)
    if not normalized_event_dates:
        return

    collection = cosmos_client.db[cosmos_client.config.EVENT_DATES_COLLECTION_NAME]
    operations = [
        ReplaceOne(
            filter={"event_date": event_date.event_date.isoformat()},
            replacement=event_date.to_dict(),
            upsert=True,
        )
        for event_date in normalized_event_dates
    ]
    collection.bulk_write(operations, ordered=False)


def get_all_event_dates() -> List[EventDate]:
    collection = cosmos_client.db[cosmos_client.config.EVENT_DATES_COLLECTION_NAME]
    docs = collection.find({})
    return sorted((EventDate.from_dict(doc) for doc in docs), key=_sort_key)


def _sort_key(event_date: EventDate) -> str:
    return event_date.event_date.isoformat()
