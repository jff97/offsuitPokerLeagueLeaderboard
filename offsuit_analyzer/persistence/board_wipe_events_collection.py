"""Board-wipe event collection operations."""
from typing import Iterable, List, Union
from datetime import date
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import BoardWipeEvent
from . import cosmos_client


def record_board_wipe_events(board_wipe_dates: Iterable[Union[str, date]]) -> None:
    """Persist distinct observed board-wipe dates keyed by the raw day."""
    normalized_board_wipe_events = sorted(
        {BoardWipeEvent(board_wipe_date=board_wipe_date) for board_wipe_date in board_wipe_dates},
        key=_sort_key,
    )
    if not normalized_board_wipe_events:
        return

    collection = cosmos_client.db[cosmos_client.config.BOARD_WIPE_EVENTS_COLLECTION_NAME]
    _migrate_legacy_board_wipe_events_if_needed(collection)
    operations = [
        ReplaceOne(
            filter={"board_wipe_date": board_wipe_event.board_wipe_date.isoformat()},
            replacement=board_wipe_event.to_dict(),
            upsert=True,
        )
        for board_wipe_event in normalized_board_wipe_events
    ]
    collection.bulk_write(operations, ordered=False)


def get_all_board_wipe_events() -> List[BoardWipeEvent]:
    collection = cosmos_client.db[cosmos_client.config.BOARD_WIPE_EVENTS_COLLECTION_NAME]
    _migrate_legacy_board_wipe_events_if_needed(collection)
    docs = collection.find({})
    return sorted({BoardWipeEvent.from_dict(doc) for doc in docs}, key=_sort_key)


def _sort_key(board_wipe_event: BoardWipeEvent) -> str:
    return board_wipe_event.board_wipe_date.isoformat()


def _get_legacy_event_dates_collection_name() -> str:
    collection_env_suffix = "Dev" if cosmos_client.config.IS_DEVELOPMENT_ENV else "Prod"
    return "eventDatesCollection" + collection_env_suffix


def _migrate_legacy_board_wipe_events_if_needed(collection) -> None:
    legacy_collection_name = _get_legacy_event_dates_collection_name()
    if legacy_collection_name == cosmos_client.config.BOARD_WIPE_EVENTS_COLLECTION_NAME:
        return

    if collection.estimated_document_count() > 0:
        return

    legacy_docs = cosmos_client.db[legacy_collection_name].find({})
    legacy_board_wipe_events = sorted({BoardWipeEvent.from_dict(doc) for doc in legacy_docs}, key=_sort_key)
    if not legacy_board_wipe_events:
        return

    collection.bulk_write(
        [
            ReplaceOne(
                filter={"board_wipe_date": board_wipe_event.board_wipe_date.isoformat()},
                replacement=board_wipe_event.to_dict(),
                upsert=True,
            )
            for board_wipe_event in legacy_board_wipe_events
        ],
        ordered=False,
    )
