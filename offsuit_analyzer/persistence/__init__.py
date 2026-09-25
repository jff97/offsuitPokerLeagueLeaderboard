"""Persistence package exports."""
from . import rounds_collection, warnings_collection, name_clashes_collection, logs_collection
from . import board_wipe_events_collection, season_windows_collection
from . import export_rounds_tool

store_rounds = rounds_collection.store_rounds
get_all_rounds = rounds_collection.get_all_rounds
get_all_round_dates = rounds_collection.get_all_round_dates
record_board_wipe_events = board_wipe_events_collection.record_board_wipe_events
get_all_board_wipe_events = board_wipe_events_collection.get_all_board_wipe_events

save_warnings = warnings_collection.save_warnings
get_all_warnings = warnings_collection.get_all_warnings
delete_all_warnings = warnings_collection.delete_all_warnings

save_these_name_clashes = name_clashes_collection.save_these_name_clashes
get_all_name_clashes = name_clashes_collection.get_all_name_clashes
delete_these_name_clashes = name_clashes_collection.delete_these_name_clashes
delete_all_name_clashes = name_clashes_collection.delete_all_name_clashes

save_log = logs_collection.save_log
save_logs = logs_collection.save_logs
get_all_logs = logs_collection.get_all_logs
get_logs_by_severity = logs_collection.get_logs_by_severity
clear_all_logs = logs_collection.clear_all_logs

email_json_rounds_backup = export_rounds_tool.email_json_rounds_backup
save_season_windows = season_windows_collection.save_season_windows
get_all_season_windows = season_windows_collection.get_all_season_windows

__all__ = [
    'store_rounds',
    'get_all_rounds',
    'get_all_round_dates',
    'record_board_wipe_events',
    'get_all_board_wipe_events',
    'save_warnings',
    'get_all_warnings',
    'delete_all_warnings',
    'save_these_name_clashes',
    'get_all_name_clashes',
    'delete_these_name_clashes',
    'delete_all_name_clashes',
    'save_log',
    'save_logs',
    'get_all_logs',
    'get_logs_by_severity',
    'clear_all_logs',
    'email_json_rounds_backup',
    'save_season_windows',
    'get_all_season_windows',
]
