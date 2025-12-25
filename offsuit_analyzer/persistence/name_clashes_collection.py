"""Name clashes collection operations."""
from typing import List
from pymongo import ReplaceOne
from offsuit_analyzer.datamodel import NameClash
from . import cosmos_client


def save_these_name_clashes(name_infos: List[NameClash]) -> None:
    if not name_infos:
        return
    
    collection = cosmos_client.db[cosmos_client.config.NAME_INFOS_COLLECTION_NAME]
    
    operations = [
        ReplaceOne(
            filter={"name": name_info.unique_id()},
            replacement=name_info.to_dict(),
            upsert=True
        )
        for name_info in name_infos
    ]
    collection.bulk_write(operations, ordered=False)


def get_all_name_clashes() -> List[NameClash]:
    collection = cosmos_client.db[cosmos_client.config.NAME_INFOS_COLLECTION_NAME]
    docs = list(collection.find({}))
    return [NameClash.from_dict(doc) for doc in docs]


def delete_these_name_clashes(name_infos: List[NameClash]) -> None:
    if not name_infos:
        return
    
    collection = cosmos_client.db[cosmos_client.config.NAME_INFOS_COLLECTION_NAME]
    names_to_delete = [name_info.name for name_info in name_infos]
    collection.delete_many({"name": {"$in": names_to_delete}})


def delete_all_name_clashes() -> None:
    collection = cosmos_client.db[cosmos_client.config.NAME_INFOS_COLLECTION_NAME]
    collection.delete_many({})
