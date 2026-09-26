"""Board-wipe event collection operations."""
from typing import List
from pymongo import ReplaceOne

from offsuit_analyzer.datamodel import BoardWipeEvent
from . import cosmos_client


def record_board_wipe_events(board_wipe_events: List[BoardWipeEvent]) -> None:
    """Save the given board-wipe events. Existing events are never modified or removed."""
    if not board_wipe_events:
        return

    collection = cosmos_client.db[cosmos_client.config.BOARD_WIPE_EVENTS_COLLECTION_NAME]
    operations = [
        ReplaceOne(
            filter={"board_wipe_date": board_wipe_event.board_wipe_date.isoformat()},
            replacement=board_wipe_event.to_dict(),
            upsert=True,
        )
        for board_wipe_event in board_wipe_events
    ]
    collection.bulk_write(operations, ordered=False)


def get_all_board_wipe_events() -> List[BoardWipeEvent]:
    collection = cosmos_client.db[cosmos_client.config.BOARD_WIPE_EVENTS_COLLECTION_NAME]
    docs = collection.find({})
    return sorted((BoardWipeEvent.from_dict(doc) for doc in docs), key=lambda board_wipe_event: board_wipe_event.board_wipe_date)
