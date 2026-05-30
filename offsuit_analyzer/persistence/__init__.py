"""Persistence package - maintains backward compatibility with existing imports."""
from . import rounds_collection, warnings_collection, name_clashes_collection
from . import export_rounds_tool

store_rounds = rounds_collection.store_rounds
get_all_rounds = rounds_collection.get_all_rounds

save_warnings = warnings_collection.save_warnings
get_all_warnings = warnings_collection.get_all_warnings
delete_all_warnings = warnings_collection.delete_all_warnings

save_these_name_clashes = name_clashes_collection.save_these_name_clashes
get_all_name_clashes = name_clashes_collection.get_all_name_clashes
delete_these_name_clashes = name_clashes_collection.delete_these_name_clashes
delete_all_name_clashes = name_clashes_collection.delete_all_name_clashes

email_json_rounds_backup = export_rounds_tool.email_json_rounds_backup

__all__ = [
    'store_rounds',
    'get_all_rounds',
    'save_warnings',
    'get_all_warnings',
    'delete_all_warnings',
    'save_these_name_clashes',
    'get_all_name_clashes',
    'delete_these_name_clashes',
    'delete_all_name_clashes',
    'email_json_rounds_backup',
]
